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

# Импорты моделей
from blogs.models import CategorysBlogs, TagsBlogs, Blogs
from projects.models import CategorysProjects, Projects
from service.models import CategorysServices, Services, ServicesFiles
from django.contrib.auth import get_user_model

User = get_user_model()
fake = Faker("ru_RU")


def random_string(n=6):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def get_or_create_author():
    """Гарантирует наличие автора"""
    author, _ = User.objects.get_or_create(
        username="testuser",
        defaults={"password": "12345"}
    )
    return author


# ==================== BLOGS ====================
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
        print(f"✅ Blog Category created: {category.name}")
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


def create_blogs(categories, tags, author, n=10):
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
    print("🚀 Начинаем заполнение базы данных...")

    # Получаем или создаем автора
    author = get_or_create_author()
    print(f"👤 Автор: {author.username}")

    # ===== BLOGS =====
    print("\n📝 Создаем категории блогов...")
    blog_categories = create_categories(5)

    print("\n🏷️ Создаем теги...")
    tags = create_tags(8)

    print("\n📄 Создаем блоги...")
    create_blogs(blog_categories, tags, author, 15)

    # ===== PROJECTS =====
    print("\n🏗️ Создаем категории проектов...")
    project_categories = create_project_categories(5)

    print("\n📊 Создаем проекты...")
    create_projects(project_categories, author, 12)

    # ===== SERVICES =====
    print("\n🛠️ Создаем категории услуг...")
    service_categories = create_service_categories(5)

    print("\n📎 Создаем файлы услуг...")
    service_files = create_service_files(8)

    print("\n📋 Создаем услуги...")
    create_services(service_categories, service_files, author, 12)

    print("\n🎉 Готово! Все тестовые данные успешно созданы.")
    print("   ✅ Блоги и теги")
    print("   ✅ Проекты и категории проектов")
    print("   ✅ Услуги и файлы услуг")