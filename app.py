from flask import Flask, render_template, abort
import os
import json
import markdown
from proper_nouns import pick_proper_nouns, PROPER_NOUNS

app = Flask(__name__)

ARTICLES_DIR = os.path.join(os.path.dirname(__file__), 'articles')

def replace_proper_nouns(article_metadata, proper_nouns):
    for article_key, article_value in article_metadata.items():
        if isinstance(article_value, str):  # Ensure the value is a string
            for proper_noun_key, proper_noun_value in proper_nouns.items():
                article_proper_noun = f'%%&&{proper_noun_key}&&%%'
                article_value_old = article_value
                article_value = article_value.replace(article_proper_noun, proper_noun_value)

                article_metadata[article_key] = article_value
    return article_metadata

def load_article(slug, proper_nouns):
    json_path = os.path.join(ARTICLES_DIR, f"{slug}.json")
    markdown_path = os.path.join(ARTICLES_DIR, f"{slug}.md")

    if not os.path.exists(json_path) or not os.path.exists(markdown_path):
        abort(404)

    with open(json_path, "r") as json_file:
        metadata = json.load(json_file)

    with open(markdown_path, "r") as markdown_file:
        body = markdown_file.read()
    metadata["body"] = body
    metadata = replace_proper_nouns(metadata, proper_nouns)
    metadata["body"] = markdown.markdown(metadata['body'])
    return metadata

@app.route("/article/<slug>")
def article(slug):
    proper_nouns = pick_proper_nouns()
    article = load_article(slug, proper_nouns)
    return render_template("article.html", article=article)

@app.route("/")
def front_page():
    articles = []
    proper_nouns = pick_proper_nouns()
    for filename in os.listdir(ARTICLES_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(ARTICLES_DIR, filename), "r") as json_file:
                metadata = json.load(json_file)
                metadata = replace_proper_nouns(metadata, proper_nouns)
                articles.append({
                    "title_frontpage": metadata["title_frontpage"],
                    "summary_frontpage": metadata["summary_frontpage"],
                    "date_created": metadata["date_created"],
                    "slug": os.path.splitext(filename)[0]
                })
    return render_template("front_page.html", articles=articles)

if __name__ == "__main__":
    app.run(debug=True)
