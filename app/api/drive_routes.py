from fastapi import APIRouter, HTTPException, Request, Response
import requests
import base64
import re
from bs4 import BeautifulSoup
from app.database import get_connection

drive_router = APIRouter()

@drive_router.get("/download")
async def download_document(file_id: str, request: Request):
    oauth_token = request.headers.get("Oauth-Token")
    email = request.headers.get("Email")
    if not oauth_token:
        raise HTTPException(status_code=401, detail="OAuth token is required")
    headers = {
        "Authorization": f"Bearer {oauth_token}"
    }
    drive_response = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType=text/html",
        headers=headers
    )
    if drive_response.status_code != 200:
        raise HTTPException(status_code=drive_response.status_code, 
                           detail="Failed to export document as HTML")
    title_response = requests.get(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=name",
        headers=headers
    )
    document_title = "Untitled Document"
    if title_response.status_code == 200:
        document_title = title_response.json().get("name", "Untitled Document")
    original_html = drive_response.text
    processed_html, image_map = process_images(original_html, file_id)
    enhanced_html = create_enhanced_html(processed_html)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        insert_doc_query = """
            INSERT INTO documents 
            (document_id, document_title, original_html, enhanced_html, user_email) 
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (document_id) DO UPDATE 
            SET document_title = EXCLUDED.document_title,
                original_html = EXCLUDED.original_html,
                enhanced_html = EXCLUDED.enhanced_html
            RETURNING id
        """
        cursor.execute(
            insert_doc_query, 
            (file_id, document_title, processed_html, enhanced_html, email)
        )
        doc_db_id = cursor.fetchone()[0]
        for img_id, img_data in image_map.items():
            insert_img_query = """
                INSERT INTO document_images
                (document_id, image_id, image_data, content_type)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (document_id, image_id) DO UPDATE
                SET image_data = EXCLUDED.image_data,
                    content_type = EXCLUDED.content_type
            """
            cursor.execute(
                insert_img_query,
                (file_id, img_id, img_data['data'], img_data['content_type'])
            )
        
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        from app.database import db_pool
        if db_pool:
            db_pool.putconn(conn)
    
    return {
        "document_id": file_id,
        "document_title": document_title,
        "original_html": processed_html,
        "enhanced_html": enhanced_html
    }

@drive_router.get("/document-image/{file_id}/{image_id}")
async def get_document_image(file_id: str, image_id: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT image_data, content_type FROM document_images
            WHERE document_id = %s AND image_id = %s
        """
        cursor.execute(query, (file_id, image_id))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Image not found")
        image_data, content_type = result
        return Response(
            content=image_data,
            media_type=content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        from app.database import db_pool
        if db_pool:
            db_pool.putconn(conn)

def process_images(html_content, file_id):
    soup = BeautifulSoup(html_content, 'html.parser')
    image_map = {}
    for i, img in enumerate(soup.find_all('img')):
        src = img.get('src', '')
        if src.startswith('data:'):
            match = re.match(r'data:([^;]+);base64,(.+)', src)
            if match:
                content_type, b64data = match.groups()
                try:
                    img_data = base64.b64decode(b64data)
                    img_id = f"img_{i}"
                    image_map[img_id] = {
                        'data': img_data,
                        'content_type': content_type
                    }
                    img['src'] = f"/api/document-image/{file_id}/{img_id}"
                except Exception as e:
                    print(f"Error processing base64 image: {e}")
        elif src.startswith(('http://', 'https://')):
            try:
                response = requests.get(src)
                if response.status_code == 200:
                    img_id = f"img_{i}"
                    content_type = response.headers.get('Content-Type', 'image/jpeg')
                    image_map[img_id] = {
                        'data': response.content,
                        'content_type': content_type
                    }
                    img['src'] = f"/api/document-image/{file_id}/{img_id}"
            except Exception as e:
                print(f"Error downloading image from {src}: {e}")
    return str(soup), image_map

def create_enhanced_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text_elements = soup.find_all(['p', 'span', 'li', 'div', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'label', 'blockquote'])
    colors = ["blue","green","red","orange"]
    for i, element in enumerate(text_elements):
        if not element.get_text(strip=True):
            continue
        current_style = element.get('style', '')
        if element.name in ['span', 'a']:
            element['style'] = f"{current_style}background-color: {colors[i % len(colors)]}; !important "
        elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            element['style'] = f"{current_style}background-color: {colors[(i+2) % len(colors)]} !important; "
        else:
            element['style'] = f"{current_style}background-color: {colors[i % len(colors)]}; !important "
    
    return str(soup)

