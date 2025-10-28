from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory post storage (temporary, no database)
POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    """
    Handle retrieving and creating posts.

    GET:
        Returns all posts as JSON.
        Optional query parameters:
            - sort: 'title' or 'content'
            - direction: 'asc' or 'desc'
    POST:
        Creates a new post.
        Requires JSON body with 'title' and 'content' fields.
    """
    if request.method == "POST":
        new_post = request.get_json()

        # Validate JSON body
        if not new_post:
            return jsonify({"error": "Request body must be JSON."}), 400

        # Check for missing or empty fields
        missing_fields = [
            field for field in ("title", "content")
            if field not in new_post or not new_post[field]
        ]

        if missing_fields:
            return jsonify({
                "error": "Missing required fields.",
                "missing": missing_fields
            }), 400

        # Generate new unique ID
        new_id = max((post["id"] for post in POSTS), default=0) + 1
        new_post["id"] = new_id

        # Add new post to list
        POSTS.append(new_post)

        # Return created post
        return jsonify(new_post), 201

    # ---- Handle GET request ----
    sort = request.args.get("sort")
    direction = request.args.get("direction")
    sorted_list = POSTS.copy()

    # Determine sorting direction
    reverse = direction == "desc" if direction in ("asc", "desc") else False

    # Validate direction
    if direction and direction not in ("asc", "desc"):
        return jsonify({
            "error": "Invalid query parameter.",
            "field": "direction",
            "allowed_values": ["asc", "desc"]
        }), 400

    # Handle sorting
    if sort:
        valid_sort_fields = {"title", "content"}
        if sort not in valid_sort_fields:
            return jsonify({
                "error": "Invalid query parameter.",
                "field": "sort",
                "allowed_values": list(valid_sort_fields)
            }), 400

        sorted_list.sort(key=lambda d: d[sort].lower(), reverse=reverse)

    # Return all posts
    return jsonify(sorted_list), 200


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete a post by its ID.

    Returns:
        200 with success message if deleted,
        404 if post not found.
    """
    # Find post by ID
    post_to_delete = next((post for post in POSTS if post["id"] == post_id), None)

    if post_to_delete is None:
        return jsonify({"error": f"No post with id {post_id} was found."}), 404

    # Remove post from list
    POSTS.remove(post_to_delete)

    # Return confirmation message
    return jsonify({
        "message": f"Post with id {post_id} has been deleted successfully."
    }), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update an existing post by its ID.

    Request body:
        JSON with optional 'title' and/or 'content' fields.
    """
    # Find the post to update
    post_to_update = next((post for post in POSTS if post["id"] == post_id), None)

    if post_to_update is None:
        return jsonify({"error": f"No post with id {post_id} was found."}), 404

    # Parse JSON body
    updates = request.get_json()
    if not updates:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    # Extract fields safely
    title = updates.get("title")
    content = updates.get("content")

    # Apply updates if provided
    if title is not None:
        post_to_update["title"] = title
    if content is not None:
        post_to_update["content"] = content

    # Return updated post and message
    return jsonify({
        "message": f"Post with id {post_id} has been updated successfully.",
        "updated_post": post_to_update
    }), 200


@app.route('/api/posts/search', methods=['GET'])
def search():
    """
    Search for posts by title or content.

    Query parameters:
        - title: partial title text (case-insensitive)
        - content: partial content text (case-insensitive)
    """
    title = request.args.get('title', '').lower()
    content = request.args.get('content', '').lower()

    # Perform case-insensitive search
    search_results = [
        post for post in POSTS
        if (title and title in post["title"].lower())
           or (content and content in post["content"].lower())
    ]

    return jsonify(search_results), 200


if __name__ == '__main__':
    # Run Flask app (debug should be disabled in production)
    app.run(host="0.0.0.0", port=5002, debug=True)
