"""Unit tests for character prototypes — no database required."""
from __future__ import annotations

import pytest

from characters.infrastructure.prototypes import (
    CharacterTemplateRegistry,
    MageTemplate,
    RogueTemplate,
    WarriorTemplate,
    build_default_registry,
)
from characters.domain.entities import TemplateNotFoundError


class TestWarriorTemplate:
    def test_warrior_has_expected_stats(self) -> None:
        warrior = WarriorTemplate()
        assert warrior.stats["strength"] == 18
        assert warrior.stats["intelligence"] == 8

    def test_warrior_clone_is_independent(self) -> None:
        original = WarriorTemplate()
        cloned = original.clone()
        # Modifying clone's stats must not affect the original
        cloned.apply_overrides({"stats": {"strength": 5}})
        assert original.stats["strength"] == 18

    def test_warrior_clone_deep_copies_skills(self) -> None:
        original = WarriorTemplate()
        cloned = original.clone()
        cloned.apply_overrides({"skills": ["new_skill"]})
        assert "sword_mastery" in original.skills

    def test_warrior_template_name(self) -> None:
        warrior = WarriorTemplate()
        assert warrior.template_name == "warrior"


class TestMageTemplate:
    def test_mage_has_high_intelligence(self) -> None:
        mage = MageTemplate()
        assert mage.stats["intelligence"] == 18

    def test_mage_clone_equipment_is_independent(self) -> None:
        mage = MageTemplate()
        cloned = mage.clone()
        cloned.apply_overrides({"equipment": ["custom_staff"]})
        assert "staff_of_power" in mage.equipment


class TestRogueTemplate:
    def test_rogue_has_high_dexterity(self) -> None:
        rogue = RogueTemplate()
        assert rogue.stats["dexterity"] == 18

    def test_rogue_starts_at_level_1(self) -> None:
        rogue = RogueTemplate()
        assert rogue.level == 1


class TestCharacterTemplateRegistry:
    def test_register_and_get(self) -> None:
        registry = CharacterTemplateRegistry()
        registry.register("warrior", WarriorTemplate())
        template = registry.get("warrior")
        assert template.template_name == "warrior"

    def test_get_unknown_template_raises(self) -> None:
        registry = CharacterTemplateRegistry()
        with pytest.raises(TemplateNotFoundError):
            registry.get("paladin")

    def test_clone_creates_independent_copy(self) -> None:
        registry = CharacterTemplateRegistry()
        registry.register("warrior", WarriorTemplate())
        clone1 = registry.clone("warrior", {"name": "Hero"})
        clone2 = registry.clone("warrior", {"name": "Villain"})
        assert clone1.name != clone2.name

    def test_clone_applies_overrides(self) -> None:
        registry = CharacterTemplateRegistry()
        registry.register("mage", MageTemplate())
        cloned = registry.clone("mage", {"name": "Gandalf", "level": 20})
        assert cloned.name == "Gandalf"
        assert cloned.level == 20

    def test_clone_does_not_modify_original(self) -> None:
        registry = CharacterTemplateRegistry()
        registry.register("warrior", WarriorTemplate())
        registry.clone("warrior", {"name": "Modified", "level": 99})
        original = registry.get("warrior")
        # Original template must remain unchanged
        assert original.level == 1

    def test_list_templates(self) -> None:
        registry = build_default_registry()
        templates = registry.list_templates()
        assert "warrior" in templates
        assert "mage" in templates
        assert "rogue" in templates

    def test_deepcopy_vs_clone_independence(self) -> None:
        """Explicitly demonstrates deepcopy creates fully independent objects."""
        import copy

        warrior = WarriorTemplate()
        # deepcopy: completely independent object
        deep_copy = copy.deepcopy(warrior)
        deep_copy._stats["strength"] = 1  # type: ignore[attr-defined]
        assert warrior.stats["strength"] == 18  # original unaffected

        # shallow copy would NOT be independent for nested dicts
        import copy as cp

        shallow = cp.copy(warrior)
        # In a shallow copy, _stats dict is shared — modifying it affects original
        # This is why we use deepcopy in clone()
        assert shallow.stats["strength"] == 18
