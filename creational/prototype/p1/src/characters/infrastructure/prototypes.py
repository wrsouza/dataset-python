"""Concrete Prototype implementations for game characters.

Each class is a ConcretePrototype that knows how to clone itself.
Uses copy.deepcopy internally with post-clone customization hooks.
"""
from __future__ import annotations

import copy
from typing import Any

from characters.domain.entities import TemplateNotFoundError
from characters.domain.interfaces import Character, CharacterRegistry


class BaseCharacter(Character):
    """Base implementation shared by all concrete character prototypes.

    Demonstrates copy.deepcopy vs custom clone:
    - copy.deepcopy creates a structurally identical deep copy
    - clone() wraps deepcopy and allows subclass-specific post-clone hooks
    """

    def __init__(
        self,
        name: str,
        template_name: str,
        stats: dict[str, int],
        skills: list[str],
        equipment: list[str],
        level: int,
    ) -> None:
        self._name = name
        self._template_name = template_name
        # Mutable containers must be independent per instance
        self._stats = dict(stats)
        self._skills = list(skills)
        self._equipment = list(equipment)
        self._level = level

    @property
    def name(self) -> str:
        return self._name

    @property
    def template_name(self) -> str:
        return self._template_name

    @property
    def stats(self) -> dict[str, int]:
        return dict(self._stats)

    @property
    def skills(self) -> list[str]:
        return list(self._skills)

    @property
    def equipment(self) -> list[str]:
        return list(self._equipment)

    @property
    def level(self) -> int:
        return self._level

    def clone(self) -> BaseCharacter:
        """Deep clone using copy.deepcopy.

        copy.deepcopy recursively copies all nested objects, ensuring the
        clone is completely independent from the original template.
        This differs from a shallow copy where nested dicts/lists
        would still point to the same memory as the original.
        """
        return copy.deepcopy(self)

    def apply_overrides(self, overrides: dict[str, Any]) -> None:
        """Apply override values after cloning.

        Called post-clone to customize the new character without
        modifying the original template.
        """
        if "name" in overrides:
            self._name = str(overrides["name"])
        if "level" in overrides:
            self._level = int(overrides["level"])
        if "stats" in overrides and isinstance(overrides["stats"], dict):
            self._stats.update(overrides["stats"])
        if "skills" in overrides and isinstance(overrides["skills"], list):
            self._skills = list(overrides["skills"])
        if "equipment" in overrides and isinstance(overrides["equipment"], list):
            self._equipment = list(overrides["equipment"])

    def to_dict(self) -> dict[str, Any]:
        """Serialize character to dictionary for API responses."""
        return {
            "name": self._name,
            "template_name": self._template_name,
            "stats": self._stats,
            "skills": self._skills,
            "equipment": self._equipment,
            "level": self._level,
        }


class WarriorTemplate(BaseCharacter):
    """Concrete Prototype for warrior-class characters.

    Warriors are melee-focused with high strength and constitution.
    """

    def __init__(self) -> None:
        super().__init__(
            name="Warrior",
            template_name="warrior",
            stats={
                "strength": 18,
                "dexterity": 10,
                "constitution": 16,
                "intelligence": 8,
                "wisdom": 10,
                "charisma": 8,
            },
            skills=["sword_mastery", "shield_block", "battle_cry", "heavy_armor"],
            equipment=["longsword", "tower_shield", "plate_armor", "health_potion"],
            level=1,
        )

    def clone(self) -> WarriorTemplate:
        """Clone warrior with deep copy, preserving warrior-specific structure."""
        cloned = copy.deepcopy(self)
        # Post-clone hook: warriors start with a fresh battle_cry cooldown
        cloned._name = f"Warrior Clone"
        return cloned


class MageTemplate(BaseCharacter):
    """Concrete Prototype for mage-class characters.

    Mages are spellcasters with high intelligence and low constitution.
    """

    def __init__(self) -> None:
        super().__init__(
            name="Mage",
            template_name="mage",
            stats={
                "strength": 6,
                "dexterity": 12,
                "constitution": 8,
                "intelligence": 18,
                "wisdom": 14,
                "charisma": 12,
            },
            skills=["fireball", "ice_lance", "arcane_shield", "mana_surge"],
            equipment=["staff_of_power", "spellbook", "mana_potion", "robe_of_arcana"],
            level=1,
        )

    def clone(self) -> MageTemplate:
        """Clone mage, ensuring the spellbook is an independent copy."""
        cloned = copy.deepcopy(self)
        cloned._name = "Mage Clone"
        return cloned


class RogueTemplate(BaseCharacter):
    """Concrete Prototype for rogue-class characters.

    Rogues are agile stealthy characters with high dexterity.
    """

    def __init__(self) -> None:
        super().__init__(
            name="Rogue",
            template_name="rogue",
            stats={
                "strength": 10,
                "dexterity": 18,
                "constitution": 12,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 14,
            },
            skills=["backstab", "stealth", "lockpick", "poison_blade"],
            equipment=["dual_daggers", "leather_armor", "smoke_bomb", "lockpicks"],
            level=1,
        )

    def clone(self) -> RogueTemplate:
        """Clone rogue with independent equipment list."""
        cloned = copy.deepcopy(self)
        cloned._name = "Rogue Clone"
        return cloned


class CharacterTemplateRegistry(CharacterRegistry):
    """Concrete PrototypeRegistry for managing character templates.

    Follows SRP: only responsible for storing and cloning templates.
    Follows OCP: new templates are registered without modifying this class.
    """

    def __init__(self) -> None:
        self._templates: dict[str, Character] = {}

    def register(self, name: str, template: Character) -> None:
        """Register a character template under the given name."""
        self._templates[name] = template

    def get(self, name: str) -> Character:
        """Retrieve a registered template by name."""
        if name not in self._templates:
            raise TemplateNotFoundError(name)
        return self._templates[name]

    def clone(self, name: str, overrides: dict[str, Any]) -> Character:
        """Clone a template and apply post-clone overrides.

        The sequence is:
        1. Retrieve template from registry
        2. Call clone() — which uses copy.deepcopy internally
        3. Apply overrides to the new independent copy
        """
        template = self.get(name)
        cloned = template.clone()
        if overrides:
            cloned.apply_overrides(overrides)
        return cloned

    def list_templates(self) -> list[str]:
        """Return all registered template names."""
        return list(self._templates.keys())


def build_default_registry() -> CharacterTemplateRegistry:
    """Factory function that builds and populates the default registry.

    Composition root: the only place that knows about concrete types.
    """
    registry = CharacterTemplateRegistry()
    registry.register("warrior", WarriorTemplate())
    registry.register("mage", MageTemplate())
    registry.register("rogue", RogueTemplate())
    return registry
