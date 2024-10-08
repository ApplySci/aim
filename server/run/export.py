"""
This module provides functionality to export tournament results to WordPress format.

It generates a zip file containing a css file and  a WordPress eXtended RSS
(WXR) file for import. The module also provides a Flask route to trigger the
export process.

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

blueprint = Blueprint('export', __name__)

css_cache = {}
all_css_content = ''


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
    css_content = ''
    for link in html_soup.find_all('link', rel='stylesheet'):
        href = link.get('href')
        if href and href.startswith('/static/'):
            css_relative_path = href[len('/static/'):]
            css_path = os.path.join(current_app.static_folder, css_relative_path)
            if css_path not in css_cache:
                try:
                    css_cache[css_path] = read_css_file(css_path)
                    all_css_content += css_cache[css_path] + '\n'
                except FileNotFoundError:
                    continue
            css_content += css_cache[css_path] + '\n'
    return css_content


def read_html_file(filepath, web_directory, tournament_short_name):
    """
    Read and process an HTML file, modifying links and content for WordPress
    compatibility.

    Args:
        filepath (str): The path to the HTML file.
        web_directory (str): The web directory path.
        tournament_short_name (str): The short name of the tournament.

    Returns:
        tuple: A tuple containing the processed HTML content and the player
               name (if found).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        get_css_content(web_directory, soup)
        main_content = soup.body
        if main_content:
            player_name = None
            h2_tag = main_content.find('h2')
            if h2_tag and h2_tag.string and h2_tag.string.startswith('Results for '):
                player_name = h2_tag.string.replace('Results for ', '')
            for script in main_content(['script']):
                script.decompose()

            for a in main_content.find_all('a', href=True):
                href = a['href']
                # Remove seating and projector links
                if 'seating' in href or 'projector' in href:
                    a.decompose()
                    continue
                # Split the href into the path and the anchor (if any)
                path, anchor = href.split('#', 1) if '#' in href else (href, '')
                
                # Remove leading slashes, 'static/', and '.html'
                path = path.lstrip('/').replace('static/', '', 1).rstrip('.html')
                
                # Remove tournament_short_name from the beginning if present
                if path.startswith(f'{tournament_short_name}/'):
                    path = path[len(f'{tournament_short_name}/'):]
                
                # Handle different types of internal links
                if path.startswith('players/'):
                    parts = path.split('/')
                    if len(parts) > 1:
                        new_href = f'/{tournament_short_name}/{parts[0]}/p{parts[-1]}'
                        a['href'] = new_href
                elif path.startswith('rounds/'):
                    parts = path.split('/')
                    if len(parts) > 1:
                        new_href = f'/{tournament_short_name}/{parts[0]}/r{parts[-1]}'
                        a['href'] = new_href
                elif path in ['index', 'ranking']:
                    a['href'] = f'/{tournament_short_name}'
                elif not path.startswith(('http://', 'https://', '#')):
                    # For any other internal link
                    a['href'] = f'/{tournament_short_name}/{path}'
                
                # Reattach the anchor if it exists
                if anchor:
                    a['href'] += f'#{anchor}'

            for img in main_content.find_all('img', src=True):
                src = img['src']
                if not src.startswith(('http://', 'https://')):
                    # Remove leading slashes and 'static/' if present
                    src = src.lstrip('/').replace('static/', '', 1)
                    img['src'] = f'/{tournament_short_name}/{src}'

            for link in main_content.find_all('link', rel='stylesheet'):
                link.decompose()
            
            wrapped_content = f'<div id="{tournament_short_name}">{str(main_content)}</div>'
            return wrapped_content, player_name
        else:
            return '', None


def modify_css_content(css_content, tournament_short_name):
    """
    Modify CSS content to include the tournament short name in selectors.

    Args:
        css_content (str): The original CSS content.
        tournament_short_name (str): The short name of the tournament.

    Returns:
        str: The modified CSS content with updated selectors.
    """
    rules = css_content.split('}')
    modified_rules = []
    for rule in rules:
        if rule.strip():
            parts = rule.split('{')
            if len(parts) == 2:
                selector, styles = parts
                modified_selector = ', '.join([f'#{tournament_short_name} {s.strip()}' for s in selector.split(',')])
                modified_rules.append(f'{modified_selector} {{{styles}}}')
    return '\n'.join(modified_rules)


def generate_wordpress_pages():
    """
    Generate WordPress pages from tournament data.

    Returns:
        list: A list of tuples containing page information (title, content,
              parent, slug, tags).
    """
    wp_pages = []
    web_directory = current_user.live_tournament.web_directory
    tournament_tag = get_tournament_short_name(web_directory)
    tournament_parent_title = tournament_tag.capitalize()
    tournament_parent_slug = tournament_tag.lower()
    wp_pages.append((tournament_parent_title, f'<div id="{tournament_tag}">Tournament: {tournament_parent_title}</div>', None, tournament_parent_slug, [tournament_tag]))
    wp_pages.append(('Players', f'<div id="{tournament_tag}">Players</div>', tournament_parent_slug, f'{tournament_parent_slug}/players', [tournament_tag]))
    wp_pages.append(('Rounds', f'<div id="{tournament_tag}">Rounds</div>', tournament_parent_slug, f'{tournament_parent_slug}/rounds', [tournament_tag]))
    main_pages = ['ranking.html']
    for page in main_pages:
        filepath = os.path.join(web_directory, page)
        if os.path.exists(filepath):
            content, _ = read_html_file(filepath, web_directory, tournament_tag)
            title = page.replace('.html', '').capitalize()
            slug = f'{tournament_parent_slug}/{title.lower()}'
            wp_pages.append((title, content, tournament_parent_slug, slug, [tournament_tag]))
    player_dir = os.path.join(web_directory, 'players')
    if os.path.exists(player_dir):
        for filename in os.listdir(player_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(player_dir, filename)
                content, player_name = read_html_file(filepath, web_directory, tournament_tag)
                player_id = filename.replace('.html', '')
                title = player_name if player_name else f'Player {player_id}'
                slug = f'{tournament_parent_slug}/players/p{player_id}'  # Changed this line
                wp_pages.append((title, content, f'{tournament_parent_slug}/players', slug, [tournament_tag]))
    round_dir = os.path.join(web_directory, 'rounds')
    if os.path.exists(round_dir):
        for filename in os.listdir(round_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(round_dir, filename)
                content, _ = read_html_file(filepath, web_directory, tournament_tag)
                round_number = filename.replace('.html', '')
                title = f'Round {round_number}'
                slug = f'{tournament_parent_slug}/rounds/r{round_number}'  # Changed this line
                wp_pages.append((title, content, f'{tournament_parent_slug}/rounds', slug, [tournament_tag]))
    return wp_pages


def generate_wordpress_wxr():
    """
    Generate WordPress eXtended RSS (WXR) content for export.

    Returns:
        str: The generated WXR content as an XML string.
    """
    rss = ET.Element('rss')
    rss.set('version', '2.0')
    rss.set('xmlns:excerpt', 'http://wordpress.org/export/1.2/excerpt/')
    rss.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')
    rss.set('xmlns:wfw', 'http://wellformedweb.org/CommentAPI/')
    rss.set('xmlns:dc', 'http://purl.org/dc/elements/1.1/')
    rss.set('xmlns:wp', 'http://wordpress.org/export/1.2/')
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'wp:wxr_version').text = '1.2'
    wp_pages = generate_wordpress_pages()
    
    # Create a set to store used slugs
    used_slugs = set()

    for title, content, parent, slug, tags in wp_pages:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = title
        ET.SubElement(item, 'link')
        ET.SubElement(item, 'pubDate').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
        ET.SubElement(item, 'dc:creator').text = 'admin'
        ET.SubElement(item, 'guid', isPermaLink='false').text = f'https://example.com/?page_id={len(used_slugs) + 1}'
        ET.SubElement(item, 'description')
        ET.SubElement(item, 'content:encoded').text = content
        ET.SubElement(item, 'excerpt:encoded')
        ET.SubElement(item, 'wp:post_id').text = str(len(used_slugs) + 1)
        ET.SubElement(item, 'wp:post_date').text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ET.SubElement(item, 'wp:post_date_gmt').text = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ET.SubElement(item, 'wp:comment_status').text = 'closed'
        ET.SubElement(item, 'wp:ping_status').text = 'closed'
        
        # Ensure unique slug
        base_slug = slug.split('/')[-1]
        unique_slug = base_slug
        counter = 1
        while unique_slug in used_slugs:
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        used_slugs.add(unique_slug)
        
        ET.SubElement(item, 'wp:post_name').text = unique_slug
        ET.SubElement(item, 'wp:status').text = 'publish'
        
        if parent is None:
            ET.SubElement(item, 'wp:post_parent').text = '0'
        else:
            parent_slug = parent.split('/')[-1]
            parent_id = [i for i, (_, _, _, s, _) in enumerate(wp_pages, 1) if s.endswith(parent_slug)][0]
            ET.SubElement(item, 'wp:post_parent').text = str(parent_id)
        
        ET.SubElement(item, 'wp:menu_order').text = '0'
        ET.SubElement(item, 'wp:post_type').text = 'page'
        ET.SubElement(item, 'wp:post_password')
        ET.SubElement(item, 'wp:is_sticky').text = '0'
        for tag in tags:
            category = ET.SubElement(item, 'category', domain='post_tag', nicename=tag)
            category.text = tag

    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent='  ')
    return xml_str


@blueprint.route('/export/wordpress')
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
    tournament_tag = get_tournament_short_name(current_user.live_tournament.web_directory)
    modified_css_content = modify_css_content(all_css_content, tournament_tag)
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        zf.writestr('wordpress_export.xml', export_data)
        zf.writestr('custom_styles.css', modified_css_content)
    memory_file.seek(0)
    response = make_response(memory_file.getvalue())
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = 'attachment; filename=wordpress_export.zip'
    return response