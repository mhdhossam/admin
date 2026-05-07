"""
Schema Registry

A singleton-style registry that holds all registered AdminSchema subclasses.
Schemas are registered either explicitly via @register or automatically
via autodiscover() which walks all installed apps for admin_schema.py modules.

Usage:
    # In apps/products/admin_schema.py
    from apps.schema.registry import registry
    from apps.schema.base import AdminSchema
    from .models import Product

    @registry.register
    class ProductSchema(AdminSchema):
        model = Product
        endpoint = "/api/products/"
        list_display = ["id", "name", "price", "created_at"]
        search_fields = ["name"]


    # In views / APIs:
    schema = registry.get("Product")      # → ProductSchema class
    all_schemas = registry.all()          # → {name: SchemaClass, ...}
    listing = registry.to_listing()       # → [{name, endpoint, label}, ...]
"""
from __future__ import annotations
import importlib
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.schema.base import AdminSchema

logger = logging.getLogger(__name__)


class SchemaRegistry:
    def __init__(self):
        self._registry: dict[str, type[AdminSchema]] = {}

    def register(self, schema_class: type[AdminSchema]) -> type[AdminSchema]:
        """
        Decorator / direct call to register a schema.

            @registry.register
            class ProductSchema(AdminSchema): ...

        or

            registry.register(ProductSchema)
        """
        name = schema_class.get_name()
        if name in self._registry:
            logger.warning("Schema '%s' is being overwritten in registry.", name)
        self._registry[name] = schema_class
        logger.debug("Registered schema: %s → %s", name, schema_class)
        return schema_class

    def get(self, name: str) -> type[AdminSchema] | None:
        """Retrieve a schema by model name (case-insensitive)."""
        # Try exact match first, then case-insensitive
        if name in self._registry:
            return self._registry[name]
        name_lower = name.lower()
        for key, val in self._registry.items():
            if key.lower() == name_lower:
                return val
        return None

    def all(self) -> dict[str, type[AdminSchema]]:
        return dict(self._registry)

    def to_listing(self) -> list[dict]:
        """
        Returns a lightweight list of all registered models for the sidebar nav.
        """
        return [
            {
                "name": name,
                "endpoint": cls.endpoint,
                "label": name,
                "url": f"/admin/{name.lower()}",
            }
            for name, cls in sorted(self._registry.items())
        ]

    def autodiscover(self):
        """
        Walk all INSTALLED_APPS and import admin_schema.py from each.
        This triggers @registry.register decorators automatically,
        mirroring how Django's admin.autodiscover() works.
        """
        from django.apps import apps as django_apps

        for app_config in django_apps.get_app_configs():
            module_path = f"{app_config.name}.admin_schema"
            try:
                importlib.import_module(module_path)
                logger.debug("Autodiscovered schema module: %s", module_path)
            except ModuleNotFoundError:
                pass
            except Exception as e:
                logger.error("Error loading schema module %s: %s", module_path, e)


# Global singleton — import this everywhere
registry = SchemaRegistry()