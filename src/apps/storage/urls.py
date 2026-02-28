from django.urls import path
app_name = 'storage'
from . import views

urlpatterns = [
    path("moderation/storage/warehouses/", views.WarehousesView.as_view(), name="warehouses_list"),
    path("moderation/storage/products/", views.ProductsView.as_view(), name="products_list"),
    path("moderation/storage/technological-maps/", views.TechnologicalMapsView.as_view(), name="technological_maps_list"),
    path("moderation/storage/warehouse-operations/", views.WarehouseOperationsView.as_view(), name="warehouse_operations_list"),
    path("moderation/storage/inventory/", views.InventoryView.as_view(), name="inventory_list"),
    path("moderation/storage/price-tags-print/", views.PriceTagsPrintView.as_view(), name="price_tags_print_list"),
    path("moderation/storage/storage-reports/", views.StorageReportsView.as_view(), name="storage_reports_list"),
    path("moderation/storage/storage-settings/", views.StorageSettingsView.as_view(), name="storage_settings_list"),
    path("moderation/storage/product-labeling/", views.ProductLabelingView.as_view(), name="product_labeling_list"),
]