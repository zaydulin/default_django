from django.shortcuts import render
from apps.useraccount.views import CustomHtmxMixin
from django.views import View


class WarehousesView(CustomHtmxMixin, View):
    template_name = 'moderation/storage/warehouses.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class ProductsView(CustomHtmxMixin, View):
    template_name = 'moderation/storage/products.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class TechnologicalMapsView(CustomHtmxMixin, View):
    template_name = 'moderation/storage/technological_maps.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class WarehouseOperationsView(CustomHtmxMixin, View):
    template_name = 'moderation/storage/warehouse_operations.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class InventoryView(CustomHtmxMixin, View):
    template_name = 'moderation/storage/inventory.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class PriceTagsPrintView(CustomHtmxMixin, View):
    template_name = 'moderation/storage/price_tags_print.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class StorageReportsView(CustomHtmxMixin, View):
    template_name = 'moderation/storage/storage_reports.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class StorageSettingsView(CustomHtmxMixin, View):
    template_name = 'moderation/storage/storage_settings.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class ProductLabelingView(CustomHtmxMixin, View):
    template_name = 'moderation/storage/product_labeling.html'

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name, context)