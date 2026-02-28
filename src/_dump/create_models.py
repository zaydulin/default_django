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
from projects.models import CategorysProjects, Projects
from services.models import CategorysServices, Services, ServicesFiles

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


# ==================== PROJECTS ====================
def create_project_categories(n=5):
    categories = []
    for _ in range(n):
        name = fake.word().capitalize() + " " + random_string()
        category = CategorysProjects.objects.create(
            name=name,
            slug=slugify(name),
            description=fake.sentence(),
            title=fake.sentence(nb_words=4),
            metadescription=fake.text(max_nb_chars=150),
            propertytitle=fake.word().capitalize(),
            propertydescription=fake.sentence(),
            publishet=True,
        )
        categories.append(category)
        print(f"✅ Project Category created: {category.name}")

    # Создаем несколько подкатегорий
    for parent in categories[:2]:
        for _ in range(2):
            name = fake.word().capitalize() + " " + random_string()
            child = CategorysProjects.objects.create(
                name=name,
                slug=slugify(name),
                description=fake.sentence(),
                parent=parent,
                title=fake.sentence(nb_words=4),
                metadescription=fake.text(max_nb_chars=150),
                propertytitle=fake.word().capitalize(),
                propertydescription=fake.sentence(),
                publishet=True,
            )
            categories.append(child)
            print(f"✅ Project Subcategory created: {child.name}")

    return categories


def create_projects(categories, author, n=10):
    projects = []
    for _ in range(n):
        name = fake.sentence(nb_words=3)
        project = Projects.objects.create(
            author=author,
            name=name,
            country=fake.country(),
            description=fake.paragraph(nb_sentences=10),
            anonce=fake.sentence(nb_words=10),
            title=fake.sentence(nb_words=4),
            metadescription=fake.text(max_nb_chars=150),
            propertytitle=fake.word().capitalize(),
            propertydescription=fake.sentence(),
            slug=slugify(name + "-" + random_string()),
            publishet=True,
            data=fake.date_this_decade(),
        )
        project.category.add(*random.sample(categories, k=min(3, len(categories))))
        projects.append(project)
        print(f"✅ Project created: {project.name}")
    return projects


# ==================== SERVICES ====================
def create_service_categories(n=5):
    categories = []
    for _ in range(n):
        name = fake.word().capitalize() + " " + random_string()
        category = CategorysServices.objects.create(
            name=name,
            slug=slugify(name),
            description=fake.sentence(),
            title=fake.sentence(nb_words=4),
            metadescription=fake.text(max_nb_chars=150),
            propertytitle=fake.word().capitalize(),
            propertydescription=fake.sentence(),
            publishet=True,
        )
        categories.append(category)
        print(f"✅ Service Category created: {category.name}")

    # Создаем подкатегории
    for parent in categories[:2]:
        for _ in range(2):
            name = fake.word().capitalize() + " " + random_string()
            child = CategorysServices.objects.create(
                name=name,
                slug=slugify(name),
                description=fake.sentence(),
                parent=parent,
                title=fake.sentence(nb_words=4),
                metadescription=fake.text(max_nb_chars=150),
                propertytitle=fake.word().capitalize(),
                propertydescription=fake.sentence(),
                publishet=True,
            )
            categories.append(child)
            print(f"✅ Service Subcategory created: {child.name}")

    return categories


def create_service_files(n=10):
    files = []
    for i in range(n):
        file_names = ['document.pdf', 'presentation.pptx', 'price.xlsx', 'brochure.pdf', 'manual.docx']
        file_obj = ServicesFiles.objects.create(
            file=f"services/files/{random.choice(file_names)}",
            name=fake.sentence(nb_words=2)
        )
        files.append(file_obj)
        print(f"✅ Service File created: {file_obj.name}")
    return files


def create_services(categories, files, author, n=10):
    services = []
    for _ in range(n):
        name = fake.sentence(nb_words=3)
        service = Services.objects.create(
            author=author,
            resource=fake.url(),
            name=name,
            description=fake.paragraph(nb_sentences=8),
            title=fake.sentence(nb_words=4),
            metadescription=fake.text(max_nb_chars=150),
            propertytitle=fake.word().capitalize(),
            propertydescription=fake.sentence(),
            slug=slugify(name + "-" + random_string()),
            publishet=True,
        )
        service.category.add(*random.sample(categories, k=min(2, len(categories))))
        service.files.add(*random.sample(files, k=min(2, len(files))))
        services.append(service)
        print(f"✅ Service created: {service.name}")
    return services


if __name__ == "__main__":
    print("🚀 Starting data generation...")
    print("=" * 50)

    # Проверяем наличие пользователей
    if not check_users():
        print("\n💡 Please create a user first using:")
        print("   python manage.py createsuperuser")
        sys.exit(1)

    # Получаем пользователя для всех создаваемых объектов
    author = get_first_user()
    if not author:
        print("❌ Cannot create data without an author")
        sys.exit(1)

    # Создаем данные для блогов
    print("\n📝 Создаем категории блогов...")
    categories = create_categories(5)

    print("\n🏷️ Создаем теги...")
    tags = create_tags(8)

    print("\n📰 Создаем блоги...")
    blogs = create_blogs(categories, tags, 15)

    # ===== PROJECTS =====
    print("\n🏗️ Создаем категории проектов...")
    project_categories = create_project_categories(5)

    print("\n📊 Создаем проекты...")
    projects = create_projects(project_categories, author, 12)

    # ===== SERVICES =====
    print("\n🛠️ Создаем категории услуг...")
    service_categories = create_service_categories(5)

    print("\n📎 Создаем файлы услуг...")
    service_files = create_service_files(8)

    print("\n📋 Создаем услуги...")
    services = create_services(service_categories, service_files, author, 12)

    print("\n" + "=" * 50)
    print("🎉 Готово! Все тестовые данные успешно созданы.")
    print("=" * 50)
    print("📊 ИТОГИ:")
    print(f"   ✅ Блоги: {len(blogs)}")
    print(f"   ✅ Категории блогов: {len(categories)}")
    print(f"   ✅ Теги: {len(tags)}")
    print(f"   ✅ Проекты: {len(projects)}")
    print(f"   ✅ Категории проектов: {len(project_categories)}")
    print(f"   ✅ Услуги: {len(services)}")
    print(f"   ✅ Категории услуг: {len(service_categories)}")
    print(f"   ✅ Файлы услуг: {len(service_files)}")
    print("=" * 50)