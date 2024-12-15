"""
This module provides functionality to export tournament results to WordPress format.

It generates a zip file containing a css file, custom_styles.css, and a WordPress eXtended RSS
(WXR) file for import, wordpress_export.xml. The module also provides a Flask route to trigger the
export process.

In your Wordpress dashboard, Tools > import > import wordpress > select the xml file

I recommend creating a specific wordpress user for the import, which will make it easier
to manage the imported content.

If you have to re-import the data, delete the existing wordpress tournament pages
AND empty the bin. And beware of caching on the server!
Otherwise the URLs get messed up - wordpress appends -2 to the slug, and messes all the links up.

"""

import os
from datetime import datetime
from bs4 import BeautifulSoup
from flask import Blueprint, make_response, current_app
from flask_login import login_required, current_user
import xml.etree.ElementTree as ET
from xml.dom import minidom
import io
import zipfile
from oauth_setup import firestore_client
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
import re

blueprint = Blueprint("export", __name__)

css_cache = {}
all_css_content = ""


def read_css_file(filepath):
    """
    Read the contents of a CSS file.

    Args:
        filepath (str): The path to the CSS file.

    Returns:
        str: The contents of the CSS file.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def get_css_content(html_soup):
    """
    Extract and cache CSS content from linked stylesheets in the HTML.

    Args:
        html_soup (BeautifulSoup): The parsed HTML content.

    Returns:
        str: The combined CSS content from all linked stylesheets.
    """
    global css_cache, all_css_content
    css_content = ""
    for link in html_soup.find_all("link", rel="stylesheet"):
        href = link.get("href")
        if href and href.startswith("/static/"):
            css_relative_path = href[len("/static/") :]
            css_path = os.path.join(current_app.static_folder, css_relative_path)
            if css_path not in css_cache:
                try:
                    css_cache[css_path] = read_css_file(css_path)
                    all_css_content += css_cache[css_path] + "\n"
                except FileNotFoundError:
                    continue
            css_content += css_cache[css_path] + "\n"
    return css_content


def preprocess_html(html_content):
    """
    Preprocess HTML content to fix common errors.
    """
    # Fix incorrectly closed h1 tags
    html_content = re.sub(
        r"<h1>([^>]*)<h1>", r"<h1>\1</h1>", html_content, flags=re.DOTALL
    )

    # Add more preprocessing steps here if needed

    return html_content


def read_html_file(filepath, tournament_short_name, is_root=False):
    """
    Read and process an HTML file, modifying links and content for WordPress
    compatibility.

    Args:
        filepath (str): The path to the HTML file.
        tournament_short_name (str): The short name of the tournament.
        is_root (bool): Whether this is the root (main tournament) page.

    Returns:
        tuple: A tuple containing the processed HTML content and the player
               name (if found).
    """
    tournament_id = current_user.live_tournament.id
    tournament_title = (
        current_user.live_tournament.title
    )  # Get the full tournament title

    with open(filepath, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Preprocess the HTML content
    html_content = preprocess_html(html_content)

    # Parse the preprocessed HTML with html5lib parser
    soup = BeautifulSoup(html_content, "html5lib")

    get_css_content(soup)
    main_content = soup.body
    if main_content:
        player_name = None

        # Add "return to final rankings" link for player and round pages
        if not is_root:
            return_link = soup.new_tag("p")
            return_a = soup.new_tag(
                "a", href=f"/t{tournament_id}_{tournament_short_name}"
            )
            return_a.string = "Return to final rankings"
            return_link.append(return_a)
            main_content.insert(0, return_link)

        # Check for and remove h1 with tournament title
        h1_tag = main_content.find("h1")
        if h1_tag and tournament_title.lower() in h1_tag.text.lower():
            h1_tag.decompose()

        h2_tag = main_content.find("h2")
        if h2_tag and h2_tag.string and h2_tag.string.startswith("Results for "):
            player_name = h2_tag.string.replace("Results for ", "")
            h2_tag.decompose()

        for script in main_content(["script"]):
            script.decompose()

        # Extract ranking link and remove nav element
        nav = main_content.find("nav")
        ranking_link = None
        if nav:
            ranking_a = nav.find(
                "a", href=lambda href: href and href.endswith("ranking.html")
            )
            if ranking_a:
                ranking_link = ranking_a
            nav.decompose()

        for a in main_content.find_all("a", href=True):
            href = a["href"]
            # Remove seating and projector links
            if "seating" in href or "projector" in href:
                a.decompose()
                continue
            # Split the href into the path and the anchor (if any)
            path, anchor = href.split("#", 1) if "#" in href else (href, "")

            # Remove leading slashes, 'static/', and '.html'
            path = path.lstrip("/").replace("static/", "", 1).rstrip(".html")

            # Remove tournament_short_name from the beginning if present
            if path.startswith(f"{tournament_short_name}/"):
                path = path[len(f"{tournament_short_name}/") :]

            # Handle different types of internal links
            if path.startswith("players/"):
                parts = path.split("/")
                if len(parts) > 1:
                    new_href = f"/t{tournament_id}_{tournament_short_name}/p{parts[-1]}"
                    a["href"] = new_href
            elif path in ["index", "ranking"]:
                if is_root:
                    a.decompose()  # Remove ranking link on root page
                else:
                    a["href"] = f"/t{tournament_id}_{tournament_short_name}"
            elif path.startswith("rounds/"):
                # Preserve round links in the ranking table
                round_number = path.split("/")[-1]
                a["href"] = f"/t{tournament_id}_{tournament_short_name}/r{round_number}"
            elif not path.startswith(("http://", "https://", "#")):
                # For any other internal link
                a["href"] = f"/t{tournament_id}_{tournament_short_name}/{path}"

            # Reattach the anchor if it exists
            if anchor:
                a["href"] += f"#{anchor}"

        for img in main_content.find_all("img", src=True):
            src = img["src"]
            if not src.startswith(("http://", "https://")):
                # Remove leading slashes and 'static/' if present
                src = src.lstrip("/").replace("static/", "", 1)
                img["src"] = f"/t{tournament_id}_{tournament_short_name}/{src}"

        for link in main_content.find_all("link", rel="stylesheet"):
            link.decompose()

        # Add ranking link in a p element if it exists
        if ranking_link:
            ranking_p = soup.new_tag("p")
            ranking_p.append(ranking_link)
            main_content.insert(0, ranking_p)

        # Safely convert main_content to string
        def safe_str(item):
            try:
                return str(item)
            except TypeError:
                return ""

        wrapped_content = f'<div id="{tournament_short_name}">{" ".join(safe_str(item) for item in main_content.contents if item)}</div>'
        return wrapped_content, player_name
    else:
        return "", None


def modify_css_content(css_content, tournament_short_name):
    """
    Modify CSS content to include the tournament short name in selectors.

    Args:
        css_content (str): The original CSS content.
        tournament_short_name (str): The short name of the tournament.

    Returns:
        str: The modified CSS content with updated selectors.
    """
    rules = css_content.split("}")
    modified_rules = []
    for rule in rules:
        if rule.strip():
            parts = rule.split("{")
            if len(parts) == 2:
                selector, styles = parts
                modified_selector = ", ".join(
                    [
                        f"#{tournament_short_name} {s.strip()}"
                        for s in selector.split(",")
                    ]
                )
                modified_rules.append(f"{modified_selector} {{{styles}}}")
    return "\n".join(modified_rules)


def get_tournament_data(firebase_id):
    ref = firestore_client.collection("tournaments").document(firebase_id)
    doc = ref.get()
    if doc.exists:
        return doc.to_dict()
    return None


def format_date(date_value):
    """
    Format a date value to 'yyyy-mm-dd HH:MM ddd' format.
    """
    if date_value:
        try:
            if isinstance(date_value, str):
                date_obj = datetime.strptime(date_value, "%Y-%m-%dT%H:%M:%S")
            elif isinstance(date_value, (datetime, DatetimeWithNanoseconds)):
                date_obj = date_value
            else:
                return str(date_value)  # Return as string if type is unknown
            return date_obj.strftime("%Y-%m-%d %H:%M %a")
        except ValueError:
            return str(date_value)  # Return original value as string if parsing fails
    return "N/A"


def generate_wordpress_pages():
    """
    Generate WordPress pages from tournament data.

    Returns:
        list: A list of tuples containing page information (title, content,
              parent, slug, tags).
    """
    wp_pages = []
    web_directory = current_user.live_tournament.web_directory
    tournament_id = current_user.live_tournament.id
    tournament_tag = current_user.live_tournament.web_directory
    tournament_parent_title = tournament_tag.capitalize()
    tournament_parent_slug = f"t{tournament_id}_{tournament_tag.lower()}"

    # Get tournament metadata from Firestore
    firebase_id = current_user.live_tournament.firebase_doc
    tournament_data = get_tournament_data(firebase_id)
    tournament_name = tournament_data.get("name", tournament_parent_title)

    # Create the main tournament page with metadata and ranking content
    image_html = ""
    if tournament_data.get("url_icon"):
        image_html = f"""
        <div class="tournament-image">
            <img src="{tournament_data['url_icon']}" alt="Tournament Icon" style="width:100px; height:100px; object-fit:cover;">
        </div>
        """

    start_date = format_date(tournament_data.get("start_date"))
    end_date = format_date(tournament_data.get("end_date"))

    metadata_content = f"""
    <div class="tournament-metadata">
        {image_html}
        <h2>Tournament Information</h2>
        <p><strong>Name:</strong> {tournament_name}</p>
        <p><strong>Start Date:</strong> {start_date}</p>
        <p><strong>End Date:</strong> {end_date}</p>
        <p><strong>Address:</strong> {tournament_data.get('address', 'N/A')}</p>
        <p><strong>Country:</strong> {tournament_data.get('country', 'N/A')}</p>
        <p><strong>Rules:</strong> {tournament_data.get('rules', 'N/A')}</p>
    </div>
    """

    # Read and process the ranking page
    ranking_filepath = os.path.join(web_directory, "ranking.html")
    ranking_content = ""
    if os.path.exists(ranking_filepath):
        ranking_content, _ = read_html_file(
            ranking_filepath, tournament_tag, is_root=True
        )

    main_content = f"""
    <div id="{tournament_tag}">
        {metadata_content}
        <h2>Rankings</h2>
        {ranking_content}
    </div>
    """
    wp_pages.append(
        (tournament_name, main_content, None, tournament_parent_slug, [tournament_tag])
    )

    player_dir = os.path.join(web_directory, "players")
    if os.path.exists(player_dir):
        for filename in os.listdir(player_dir):
            if filename.endswith(".html"):
                filepath = os.path.join(player_dir, filename)
                content, player_name = read_html_file(filepath, tournament_tag)
                player_id = filename.replace(".html", "")
                title = (
                    f"{tournament_name} - {player_name}"
                    if player_name
                    else f"{tournament_name} - Player {player_id}"
                )
                slug = f"{tournament_parent_slug}/p{player_id}"
                wp_pages.append(
                    (title, content, tournament_parent_slug, slug, [tournament_tag])
                )

    rounds_dir = os.path.join(web_directory, "rounds")
    if os.path.exists(rounds_dir):
        for filename in os.listdir(rounds_dir):
            if filename.endswith(".html"):
                filepath = os.path.join(rounds_dir, filename)
                content, _ = read_html_file(filepath, tournament_tag)
                round_name = filename.replace(".html", "")
                title = f"{tournament_name} - Round {round_name}"
                slug = f"{tournament_parent_slug}/r{round_name}"
                wp_pages.append(
                    (title, content, tournament_parent_slug, slug, [tournament_tag])
                )

    return wp_pages


def generate_wordpress_wxr():
    """
    Generate WordPress eXtended RSS (WXR) content for export.

    Returns:
        str: The generated WXR content as an XML string.
    """
    rss = ET.Element("rss")
    rss.set("version", "2.0")
    rss.set("xmlns:excerpt", "http://wordpress.org/export/1.2/excerpt/")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
    rss.set("xmlns:wfw", "http://wellformedweb.org/CommentAPI/")
    rss.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
    rss.set("xmlns:wp", "http://wordpress.org/export/1.2/")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "wp:wxr_version").text = "1.2"
    wp_pages = generate_wordpress_pages()

    # Create a set to store used slugs
    used_slugs = set()

    for title, content, parent, slug, tags in wp_pages:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link")
        ET.SubElement(item, "pubDate").text = datetime.now().strftime(
            "%a, %d %b %Y %H:%M:%S +0000"
        )
        ET.SubElement(item, "dc:creator").text = "admin"
        ET.SubElement(item, "guid", isPermaLink="false").text = (
            f"https://example.com/?page_id={len(used_slugs) + 1}"
        )
        ET.SubElement(item, "description")
        ET.SubElement(item, "content:encoded").text = content
        ET.SubElement(item, "excerpt:encoded")
        ET.SubElement(item, "wp:post_id").text = str(len(used_slugs) + 1)
        ET.SubElement(item, "wp:post_date").text = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        ET.SubElement(item, "wp:post_date_gmt").text = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        ET.SubElement(item, "wp:comment_status").text = "closed"
        ET.SubElement(item, "wp:ping_status").text = "closed"

        # Ensure unique slug
        base_slug = slug.split("/")[-1]
        unique_slug = base_slug
        counter = 1
        while unique_slug in used_slugs:
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        used_slugs.add(unique_slug)

        ET.SubElement(item, "wp:post_name").text = unique_slug
        ET.SubElement(item, "wp:status").text = "publish"

        if parent is None:
            ET.SubElement(item, "wp:post_parent").text = "0"
        else:
            parent_slug = parent.split("/")[-1]
            parent_id = [
                i
                for i, (_, _, _, s, _) in enumerate(wp_pages, 1)
                if s.endswith(parent_slug)
            ][0]
            ET.SubElement(item, "wp:post_parent").text = str(parent_id)

        ET.SubElement(item, "wp:menu_order").text = "0"
        ET.SubElement(item, "wp:post_type").text = "page"
        ET.SubElement(item, "wp:post_password")
        ET.SubElement(item, "wp:is_sticky").text = "0"
        for tag in tags:
            category = ET.SubElement(item, "category", domain="post_tag", nicename=tag)
            category.text = tag

    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
    return xml_str


@blueprint.route("/export/wordpress")
@login_required
def export_wordpress():
    """
    Flask route to handle WordPress export.

    Returns:
        Response: A Flask response containing a ZIP file with the WXR and CSS
                  content.
    """
    global all_css_content
    export_data = generate_wordpress_wxr()
    tournament_tag = current_user.live_tournament.web_directory
    modified_css_content = modify_css_content(all_css_content, tournament_tag)
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, "w") as zf:
        zf.writestr("wordpress_export.xml", export_data)
        zf.writestr("custom_styles.css", modified_css_content)
    memory_file.seek(0)
    response = make_response(memory_file.getvalue())
    response.headers["Content-Type"] = "application/zip"
    response.headers["Content-Disposition"] = (
        "attachment; filename=wordpress_export.zip"
    )
    return response
