import os
import sys
import django
import random
import string
from contextlib import contextmanager
from django.utils.text import slugify
from faker import Faker

# Путь до проекта
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_project.settings")


@contextmanager
def suppress_logging():
    """Временно отключаем логирование"""
    import logging
    logging.disable(logging.CRITICAL)
    try:
        yield
    finally:
        logging.disable(logging.NOTSET)


# Инициализируем Django с отключенным логированием
with suppress_logging():
    django.setup()

# Импортируем модели
from django.contrib.auth import get_user_model
from blogs.models import CategorysBlogs, TagsBlogs, Blogs

User = get_user_model()
fake = Faker("ru_RU")


def random_string(n=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def get_first_user():
    """Получаем первого пользователя из базы данных"""
    user = User.objects.first()
    if not user:
        print("⚠️ No users found in database. Please create a user first.")
        return None
    print(f"✅ Using author: {user.username} (ID: {user.id})")
    return user


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
    # Получаем первого пользователя
    author = get_first_user()
    if not author:
        print("❌ Cannot create blogs without an author")
        return []

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


def check_users():
    """Проверяем наличие пользователей в базе"""
    users = User.objects.all()
    if users.exists():
        print(f"📊 Found {users.count()} user(s) in database:")
        for user in users:
            print(f"   - {user.username} (ID: {user.id})")
        return True
    else:
        print("❌ No users found in database!")
        return False


if __name__ == "__main__":
    print("🚀 Starting data generation...")
    print("=" * 50)

    # Проверяем наличие пользователей
    if not check_users():
        print("\n💡 Please create a user first using:")
        print("   python manage.py createsuperuser")
        sys.exit(1)

    # Создаем данные
    categories = create_categories(5)
    tags = create_tags(8)
    blogs = create_blogs(categories, tags, 15)

    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   Categories created: {len(categories)}")
    print(f"   Tags created: {len(tags)}")
    print(f"   Blogs created: {len(blogs)}")
    print("=" * 50)
    print("🎉 Done! Тестовые данные созданы.")