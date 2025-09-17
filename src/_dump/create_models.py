import os
import sys
import django
import random
import string
from django.utils.text import slugify
from faker import Faker

# --- Django setup ---
# Путь до проекта (где settings.py)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project.settings")  # замени на свой settings.py

# Отключаем конфигурацию логов, если settings.py пытается включить file handler
import logging.config
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "WARNING"},
})

django.setup()

from blogs.models import CategorysBlogs, TagsBlogs, Blogs
from django.contrib.auth import get_user_model

User = get_user_model()
fake = Faker("ru_RU")


def random_string(n=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def create_categories(n=5):
    categories = []
    for _ in range(n):
        name = fake.word().capitalize() + " " + random_string()
        category = CategorysBlogs.objects.create(
            name=name,
            slug=slugify(name),
            description=fake.sentence(),
            publishet=True,
        )
        categories.append(category)
        print(f"✅ Category created: {category.name}")
    return categories


def create_tags(n=10):
    tags = []
    for _ in range(n):
        name = fake.word().capitalize() + " " + random_string()
        tag = TagsBlogs.objects.create(
            name=name,
            slug=slugify(name),
            description=fake.sentence(),
            publishet=True,
        )
        tags.append(tag)
        print(f"✅ Tag created: {tag.name}")
    return tags


def create_blogs(categories, tags, n=10):
    # гарантируем автора
    author, _ = User.objects.get_or_create(
        username="testuser", defaults={"password": "12345"}
    )
    blogs = []
    for _ in range(n):
        name = fake.sentence(nb_words=4)
        blog = Blogs.objects.create(
            author=author,
            resource=fake.domain_name(),
            name=name,
            description=fake.paragraph(nb_sentences=5),
            title=fake.sentence(nb_words=6),
            metadescription=fake.text(max_nb_chars=150),
            propertytitle=fake.word().capitalize(),
            propertydescription=fake.sentence(),
            slug=slugify(name + "-" + random_string()),
            publishet=True,
        )
        blog.category.add(*random.sample(categories, k=min(2, len(categories))))
        blog.tags.add(*random.sample(tags, k=min(3, len(tags))))
        blogs.append(blog)
        print(f"✅ Blog created: {blog.name}")
    return blogs


if __name__ == "__main__":
    categories = create_categories(5)
    tags = create_tags(8)
    create_blogs(categories, tags, 15)
    print("🎉 Done! Тестовые данные созданы.")
