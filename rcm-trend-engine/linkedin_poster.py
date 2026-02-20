#!/usr/bin/env python3
"""
LinkedIn Poster — Post text or documents to RevCycleAI company page
"""

import sys
import json
import requests
import base64
from pathlib import Path

BASE_DIR = Path(__file__).parent
TOKEN_FILE = BASE_DIR / ".linkedin_token.json"


def load_token():
    """Load access token from file"""
    if not TOKEN_FILE.exists():
        print("❌ No access token found. Run linkedin_auth.py first.")
        sys.exit(1)
    
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    
    return data.get("access_token")


def get_organization_urn(token):
    """Get the Organization URN for the RevCycleAI company page"""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    try:
        response = requests.get(
            "https://api.linkedin.com/v2/organizationAcls?q=roleAssignee&projection=(elements*(organization~(localizedName)))",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get organization: {response.status_code}")
            print(response.text)
            sys.exit(1)
        
        data = response.json()
        
        # Find RevCycleAI
        for elem in data.get("elements", []):
            org = elem.get("organization~", {})
            name = org.get("localizedName")
            if name and "RevCycle" in name:
                urn = elem.get("organization")
                print(f"✅ Found organization: {name} → {urn}")
                return urn
        
        print("❌ RevCycleAI organization not found. Organizations available:")
        for elem in data.get("elements", []):
            org = elem.get("organization~", {})
            print(f"  - {org.get('localizedName')}")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Failed to get organization: {e}")
        sys.exit(1)


def post_text(token, org_urn, text):
    """Post a text-only update to the company page"""
    payload = {
        "author": org_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    try:
        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            json=payload,
            headers=headers
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Post failed: {response.status_code}")
            print(response.text)
            sys.exit(1)
        
        result = response.json()
        print(f"✅ Post published: {result.get('id')}")
        return result
    
    except Exception as e:
        print(f"❌ Post failed: {e}")
        sys.exit(1)


def post_document(token, org_urn, pdf_path, caption):
    """Post a document (PDF carousel) to the company page"""
    # Step 1: Register the upload
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-document"],
            "owner": org_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    try:
        # Step 1: Register upload
        response = requests.post(
            "https://api.linkedin.com/v2/assets?action=registerUpload",
            json=payload,
            headers=headers
        )
        
        if response.status_code not in [200, 201]:
            print(f"❌ Upload registration failed: {response.status_code}")
            print(response.text)
            sys.exit(1)
        
        upload_data = response.json()
        asset_urn = upload_data["value"]["asset"]
        upload_url = upload_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        
        # Step 2: Upload the PDF
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        upload_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/pdf"
        }
        
        upload_response = requests.put(upload_url, data=pdf_bytes, headers=upload_headers)
        
        if upload_response.status_code not in [200, 201]:
            print(f"❌ PDF upload failed: {upload_response.status_code}")
            print(upload_response.text)
            sys.exit(1)
        
        # Step 3: Post the document
        post_payload = {
            "author": org_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": caption
                    },
                    "shareMediaCategory": "DOCUMENT",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": "RevCycleAI Weekly Carousel"
                            },
                            "media": asset_urn,
                            "title": {
                                "text": "This Week in RCM"
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        post_response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            json=post_payload,
            headers=headers
        )
        
        if post_response.status_code not in [200, 201]:
            print(f"❌ Document post failed: {post_response.status_code}")
            print(post_response.text)
            sys.exit(1)
        
        result = post_response.json()
        print(f"✅ Document post published: {result.get('id')}")
        return result
    
    except Exception as e:
        print(f"❌ Document post failed: {e}")
        sys.exit(1)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Post to RevCycleAI LinkedIn page")
    parser.add_argument("--text", help="Text post content")
    parser.add_argument("--document", help="Path to PDF for document post")
    parser.add_argument("--caption", help="Caption for document post")
    parser.add_argument("--get-org", action="store_true", help="Get organization URN and exit")
    args = parser.parse_args()
    
    token = load_token()
    
    if args.get_org:
        get_organization_urn(token)
        return
    
    org_urn = get_organization_urn(token)
    
    if args.document:
        if not args.caption:
            print("❌ --caption required for document posts")
            sys.exit(1)
        post_document(token, org_urn, args.document, args.caption)
    elif args.text:
        post_text(token, org_urn, args.text)
    else:
        print("❌ Specify --text or --document")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
