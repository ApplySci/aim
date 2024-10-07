"""
This module provides functionality to export tournament data to WordPress format.

It includes functions to read HTML and CSS files, modify content for WordPress compatibility,
generate WordPress pages, and create a WordPress eXtended RSS (WXR) file for import.
The module also provides a Flask route to trigger the export process.
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

blueprint = Blueprint('export', __name__)

def get_tournament_short_name(web_directory):
    """
    Extract the tournament short name from the web directory path.

    Args:
        web_directory (str): The web directory path.

    Returns:
        str: The tournament short name, or None if not found.
    """
    parts = web_directory.split('static/', 1)
    if len(parts) > 1:
        return parts[1].split('/', 1)[0]
    return None

def read_css_file(filepath):
    """
    Read the contents of a CSS file.

    Args:
        filepath (str): The path to the CSS file.

    Returns:
        str: The contents of the CSS file.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

css_cache = {}
all_css_content = ""

def get_css_content(web_directory, html_soup):
    """
    Extract and cache CSS content from linked stylesheets in the HTML.

    Args:
        web_directory (str): The web directory path.
        html_soup (BeautifulSoup): The parsed HTML content.

    Returns:
        str: The combined CSS content from all linked stylesheets.
    """
    global css_cache, all_css_content
    css_content = ""
    
    for link in html_soup.find_all('link', rel='stylesheet'):
        href = link.get('href')
        if href and href.startswith('/static/'):
            css_relative_path = href[len('/static/'):]
            css_path = os.path.join(current_app.static_folder, css_relative_path)
            
            if css_path not in css_cache:
                try:
                    css_cache[css_path] = read_css_file(css_path)
                    all_css_content += css_cache[css_path] + "\n"
                except FileNotFoundError:
                    continue
            css_content += css_cache[css_path] + "\n"
    
    return css_content

def read_html_file(filepath, web_directory, tournament_short_name):
    """
    Read and process an HTML file, modifying links and content for WordPress compatibility.

    Args:
        filepath (str): The path to the HTML file.
        web_directory (str): The web directory path.
        tournament_short_name (str): The short name of the tournament.

    Returns:
        tuple: A tuple containing the processed HTML content and the player name (if found).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
        get_css_content(web_directory, soup)
        
        main_content = soup.body
        
        if main_content:
            # Extract player name if it exists
            player_name = None
            h2_tag = main_content.find('h2')
            if h2_tag and h2_tag.string and h2_tag.string.startswith('Results for '):
                player_name = h2_tag.string.replace('Results for ', '')
            
            for script in main_content(["script"]):
                script.decompose()
            
            for a in main_content.find_all('a', href=True):
                href = a['href']
                if href.endswith('seating.html') or href.endswith('projector.html'):
                    a.decompose()
                else:
                    # Remove any existing tournament_short_name from the beginning of the href
                    while href.startswith(f'/{tournament_short_name}/'):
                        href = href[len(f'/{tournament_short_name}'):]
                    
                    # Remove '/static/' if it's at the start of the href
                    if href.startswith('/static/'):
                        href = href[len('/static/'):]
                    
                    # Adjust URLs for player and round pages
                    if href.startswith('players/') or href.startswith('rounds/'):
                        parts = href.split('/')
                        if parts[0] == 'players':
                            new_href = f"/{tournament_short_name}/players/player-{parts[-1].replace('.html', '')}/"
                        else:  # rounds
                            new_href = f"/{tournament_short_name}/rounds/round-{parts[-1].replace('.html', '')}/"
                        a['href'] = new_href
                    elif href.startswith('/'):
                        a['href'] = f"/{tournament_short_name}{href}"
                    elif href.startswith('http'):
                        # For external links, keep them as is
                        pass
                    else:
                        # For relative links, add the tournament short name
                        a['href'] = f"/{tournament_short_name}/{href}"
            
            for img in main_content.find_all('img', src=True):
                src = img['src']
                if src.startswith('/static/'):
                    img['src'] = f"/{tournament_short_name}{src.replace('/static/', '/', 1)}"
                elif not src.startswith(('http://', 'https://')):
                    img['src'] = f"/{tournament_short_name}/{src}"
            
            for link in main_content.find_all('link', rel='stylesheet'):
                link.decompose()
            
            # Wrap the content in a div with the tournament's short name as the ID
            wrapped_content = f'<div id="{tournament_short_name}">{str(main_content)}</div>'
            
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
    # Split the CSS content into individual rules
    rules = css_content.split('}')
    
    modified_rules = []
    for rule in rules:
        if rule.strip():
            # Split each rule into selector and styles
            parts = rule.split('{')
            if len(parts) == 2:
                selector, styles = parts
                # Prefix each selector with the tournament's short name ID
                modified_selector = ', '.join([f'#{tournament_short_name} {s.strip()}' for s in selector.split(',')])
                modified_rules.append(f'{modified_selector} {{{styles}}}')
    
    return '\n'.join(modified_rules)

def generate_wordpress_pages():
    """
    Generate WordPress pages from tournament data.

    Returns:
        list: A list of tuples containing page information (title, content, parent, slug, tags).
    """
    wp_pages = []
    web_directory = current_user.live_tournament.web_directory
    tournament_tag = get_tournament_short_name(web_directory)

    # Create a parent page for the tournament
    tournament_parent_title = tournament_tag.capitalize()
    tournament_parent_slug = tournament_tag.lower()
    wp_pages.append((tournament_parent_title, f"<div id='{tournament_tag}'>Tournament: {tournament_parent_title}</div>", None, tournament_parent_slug, [tournament_tag]))

    # Create 'Players' page
    wp_pages.append(("Players", "<div id='{tournament_tag}'>Players</div>", tournament_parent_slug, f"{tournament_parent_slug}/players", [tournament_tag]))

    # Create 'Rounds' page
    wp_pages.append(("Rounds", "<div id='{tournament_tag}'>Rounds</div>", tournament_parent_slug, f"{tournament_parent_slug}/rounds", [tournament_tag]))

    main_pages = ['ranking.html']
    for page in main_pages:
        filepath = os.path.join(web_directory, page)
        if os.path.exists(filepath):
            content, _ = read_html_file(filepath, web_directory, tournament_tag)
            title = page.replace('.html', '').capitalize()
            slug = f"{tournament_parent_slug}/{title.lower()}"
            wp_pages.append((title, content, tournament_parent_slug, slug, [tournament_tag]))

    player_dir = os.path.join(web_directory, "players")
    if os.path.exists(player_dir):
        for filename in os.listdir(player_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(player_dir, filename)
                content, player_name = read_html_file(filepath, web_directory, tournament_tag)
                player_id = filename.replace('.html', '')
                title = player_name if player_name else f"Player {player_id}"
                slug = f"{tournament_parent_slug}/players/player-{player_id}"
                wp_pages.append((title, content, f"{tournament_parent_slug}/players", slug, [tournament_tag]))

    round_dir = os.path.join(web_directory, "rounds")
    if os.path.exists(round_dir):
        for filename in os.listdir(round_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(round_dir, filename)
                content, _ = read_html_file(filepath, web_directory, tournament_tag)
                round_number = filename.replace('.html', '')
                title = f"Round {round_number}"
                slug = f"{tournament_parent_slug}/rounds/round-{round_number}"
                wp_pages.append((title, content, f"{tournament_parent_slug}/rounds", slug, [tournament_tag]))

    return wp_pages

def generate_wordpress_wxr():
    """
    Generate WordPress eXtended RSS (WXR) content for export.

    Returns:
        str: The generated WXR content as an XML string.
    """
    rss = ET.Element('rss')
    rss.set('version', '2.0')
    rss.set('xmlns:excerpt', "http://wordpress.org/export/1.2/excerpt/")
    rss.set('xmlns:content', "http://purl.org/rss/1.0/modules/content/")
    rss.set('xmlns:wfw', "http://wellformedweb.org/CommentAPI/")
    rss.set('xmlns:dc', "http://purl.org/dc/elements/1.1/")
    rss.set('xmlns:wp', "http://wordpress.org/export/1.2/")

    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'wp:wxr_version').text = '1.2'

    wp_pages = generate_wordpress_pages()

    # Create a dictionary to store page IDs
    page_ids = {}
    current_id = 1

    # First pass: create all pages and store their IDs
    for title, content, parent, slug, tags in wp_pages:
        page_ids[slug] = current_id
        current_id += 1

    # Second pass: create the actual XML structure with correct parent references
    for title, content, parent, slug, tags in wp_pages:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = title
        ET.SubElement(item, 'link')
        ET.SubElement(item, 'pubDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
        ET.SubElement(item, 'dc:creator').text = 'admin'
        ET.SubElement(item, 'guid', isPermaLink="false").text = f"https://example.com/?page_id={page_ids[slug]}"
        ET.SubElement(item, 'description')
        ET.SubElement(item, 'content:encoded').text = content
        ET.SubElement(item, 'excerpt:encoded')
        ET.SubElement(item, 'wp:post_id').text = str(page_ids[slug])
        ET.SubElement(item, 'wp:post_date').text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ET.SubElement(item, 'wp:post_date_gmt').text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ET.SubElement(item, 'wp:comment_status').text = 'closed'
        ET.SubElement(item, 'wp:ping_status').text = 'closed'
        ET.SubElement(item, 'wp:post_name').text = slug.split('/')[-1]  # Use only the last part of the slug
        ET.SubElement(item, 'wp:status').text = 'publish'
        
        # Handle parent pages correctly
        if parent is None:
            ET.SubElement(item, 'wp:post_parent').text = '0'
        else:
            parent_id = page_ids.get(parent, 0)
            ET.SubElement(item, 'wp:post_parent').text = str(parent_id)
        
        ET.SubElement(item, 'wp:menu_order').text = '0'
        ET.SubElement(item, 'wp:post_type').text = 'page'
        ET.SubElement(item, 'wp:post_password')
        ET.SubElement(item, 'wp:is_sticky').text = '0'
        for tag in tags:
            category = ET.SubElement(item, 'category', domain="post_tag", nicename=tag)
            category.text = tag

    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
    return xml_str

@blueprint.route('/export/wordpress')
@login_required
def export_wordpress():
    """
    Flask route to handle WordPress export.

    Returns:
        Response: A Flask response containing a ZIP file with the WXR and CSS content.
    """
    global all_css_content
    export_data = generate_wordpress_wxr()
    
    # Modify CSS content to include tournament short name in selectors
    tournament_tag = get_tournament_short_name(current_user.live_tournament.web_directory)
    modified_css_content = modify_css_content(all_css_content, tournament_tag)
    
    # Create a ZIP file containing both the WXR and CSS files
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        zf.writestr('wordpress_export.xml', export_data)
        zf.writestr('custom_styles.css', modified_css_content)
    
    memory_file.seek(0)
    
    response = make_response(memory_file.getvalue())
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = 'attachment; filename=wordpress_export.zip'
    
    return response