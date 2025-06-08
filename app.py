from flask import Flask, render_template, abort
import os
import json
import markdown

app = Flask(__name__)

ARTICLES_DIR = "/home/rayhan/dev/internetnewswebsite.com/articles"

def load_article(slug):
    json_path = os.path.join(ARTICLES_DIR, f"{slug}.json")
    markdown_path = os.path.join(ARTICLES_DIR, f"{slug}.md")

    if not os.path.exists(json_path) or not os.path.exists(markdown_path):
        abort(404)

    with open(json_path, "r") as json_file:
        metadata = json.load(json_file)

    with open(markdown_path, "r") as markdown_file:
        body = markdown_file.read()

    metadata["body"] = markdown.markdown(body)
    return metadata

@app.route("/article/<slug>")
def article(slug):
    article = load_article(slug)
    return render_template("article.html", article=article)

@app.route("/")
def front_page():
    articles = []
    for filename in os.listdir(ARTICLES_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(ARTICLES_DIR, filename), "r") as json_file:
                metadata = json.load(json_file)
                articles.append({
                    "title": metadata["title"],
                    "summary_sm": metadata["summary_sm"],
                    "date_created": metadata["date_created"],
                    "slug": os.path.splitext(filename)[0]
                })
    return render_template("front_page.html", articles=articles)

if __name__ == "__main__":
    app.run(debug=True)
