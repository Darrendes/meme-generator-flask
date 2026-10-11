from pathlib import Path
import os
import uuid

from flask import Flask, render_template, request, redirect, send_file, abort, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
GENERATED_DIR = BASE_DIR / "static" / "generated"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "local-demo-key-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR / 'memes.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit

db = SQLAlchemy(app)
ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP"}


class Meme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    top_text = db.Column(db.String(255), default="")
    bottom_text = db.Column(db.String(255), default="")


def create_meme_image(source_path: Path, output_path: Path, top_text: str, bottom_text: str) -> None:
    with Image.open(source_path) as source:
        if source.format not in ALLOWED_FORMATS:
            raise ValueError("Format d’image non pris en charge.")
        image = source.convert("RGB")

    draw = ImageDraw.Draw(image)
    width, height = image.size
    font_size = max(20, min(64, width // 12))

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    def draw_text_with_outline(text: str, y: int) -> None:
        if not text:
            return
        text = text.upper()[:120]
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=2)
        text_width = bbox[2] - bbox[0]
        x = max(5, (width - text_width) // 2)
        draw.text((x, y), text, font=font, fill="white", stroke_width=3, stroke_fill="black")

    draw_text_with_outline(top_text, 15)
    draw_text_with_outline(bottom_text, max(15, height - font_size - 20))
    image.save(output_path, format="PNG")


@app.route("/")
def index():
    memes = Meme.query.order_by(Meme.id.desc()).all()
    return render_template("index.html", memes=memes)


@app.route("/generate", methods=["POST"])
def generate():
    uploaded = request.files.get("image")
    if uploaded is None or not uploaded.filename:
        flash("Sélectionnez une image avant de continuer.", "error")
        return redirect(url_for("index"))

    top_text = request.form.get("top_text", "").strip()[:120]
    bottom_text = request.form.get("bottom_text", "").strip()[:120]
    filename = f"{uuid.uuid4().hex}.png"
    source_path = UPLOAD_DIR / f"{uuid.uuid4().hex}.upload"
    output_path = GENERATED_DIR / filename

    try:
        uploaded.save(source_path)
        # Pillow verifies the actual image format, not only the filename extension.
        with Image.open(source_path) as image:
            image.verify()
        create_meme_image(source_path, output_path, top_text, bottom_text)
    except (UnidentifiedImageError, OSError, ValueError):
        source_path.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)
        flash("Le fichier envoyé n’est pas une image prise en charge.", "error")
        return redirect(url_for("index"))
    finally:
        source_path.unlink(missing_ok=True)

    meme = Meme(filename=filename, top_text=top_text, bottom_text=bottom_text)
    db.session.add(meme)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/download/<int:meme_id>")
def download(meme_id):
    meme = Meme.query.get_or_404(meme_id)
    path = GENERATED_DIR / meme.filename
    if not path.is_file():
        abort(404)
    return send_file(path, as_attachment=True, download_name=f"meme_{meme.id}.png")


@app.route("/delete/<int:meme_id>", methods=["POST"])
def delete(meme_id):
    meme = Meme.query.get_or_404(meme_id)
    (GENERATED_DIR / meme.filename).unlink(missing_ok=True)
    db.session.delete(meme)
    db.session.commit()
    flash("Mème supprimé.", "success")
    return redirect(url_for("index"))


@app.errorhandler(413)
def request_entity_too_large(_error):
    return "Le fichier dépasse la limite de 10 Mo.", 413


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # Debug is disabled by default for safer local demonstrations.
    app.run(debug=False)
