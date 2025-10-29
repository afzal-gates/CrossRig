# Mixanimo Lite - Clean Architecture Documentation

## Overview

Mixanimo Lite has been refactored to follow **Clean Architecture** and **SOLID** principles, transforming from a monolithic 989-line file into a well-organized, maintainable structure.

## Architecture Layers

```
Mixanimo_Lite/
├── __init__.py                  # Main entry point (50 lines)
├── config/                      # Configuration layer
│   ├── __init__.py
│   └── constants.py             # All constants and default values
├── core/                        # Core business logic (Framework-independent)
│   ├── domain/                  # Domain layer (Pure Python)
│   │   ├── __init__.py
│   │   ├── entities.py          # Data structures (ActionItem, AnimationSettings)
│   │   └── math_utils.py        # Pure math functions (rotation, offsets)
│   ├── services/                # Service layer
│   │   ├── __init__.py
│   │   └── action_service.py    # Action manipulation services
│   ├── use_cases/               # Use case layer
│   │   ├── __init__.py
│   │   ├── send_to_timeline.py  # NLA sequencing logic
│   │   ├── bake_animation.py    # Animation baking logic
│   │   ├── stabilize_root.py    # Root stabilization logic
│   │   └── export_fbx.py        # FBX export logic
│   └── __init__.py
└── adapters/                    # Adapter layer (Blender-specific)
    ├── blender/
    │   ├── __init__.py
    │   ├── properties.py        # Blender PropertyGroups
    │   ├── operators.py         # Blender Operators
    │   ├── panels.py            # Blender UI Panels
    │   └── handlers.py          # Blender event handlers
    └── __init__.py
```

## Layer Responsibilities

### 1. Configuration Layer (`config/`)
**Purpose**: Centralized configuration and constants

- **No dependencies**: Pure Python constants
- **Single source of truth** for default values, limits, naming conventions
- **Easy to modify** settings without touching business logic

**Files**:
- `constants.py`: All magic numbers, default values, FBX settings

### 2. Domain Layer (`core/domain/`)
**Purpose**: Pure business entities and value objects

- **No Blender dependencies**: Can be tested independently
- **No side effects**: Pure functions and data structures
- **Core concepts**: ActionItem, AnimationSettings, mathematical operations

**Files**:
- `entities.py`: Data classes representing core concepts
- `math_utils.py`: Pure mathematical functions (rotation, vectors)

**SOLID Principles**:
- **Single Responsibility**: Each entity/function has one purpose
- **Open/Closed**: Easy to extend without modification
- **Dependency Inversion**: No dependencies on frameworks

### 3. Services Layer (`core/services/`)
**Purpose**: Business logic services for action manipulation

- **Minimal Blender coupling**: Uses Blender objects but not UI
- **Reusable logic**: Can be called from different contexts
- **Testable**: Business logic separated from UI

**Files**:
- `action_service.py`: FCurve manipulation, action copying, trajectory rotation

**SOLID Principles**:
- **Single Responsibility**: Each function does one thing
- **Interface Segregation**: Small, focused functions
- **Liskov Substitution**: Compatible with Blender action API

### 4. Use Cases Layer (`core/use_cases/`)
**Purpose**: Application-specific business rules

- **Orchestration**: Coordinates services to accomplish tasks
- **Transaction boundaries**: Manages Blender state changes
- **Error handling**: Returns success/failure tuples
- **Context-aware**: Uses Blender context when needed

**Files**:
- `send_to_timeline.py`: Sequences actions to NLA timeline
- `bake_animation.py`: Bakes NLA strips to single action
- `stabilize_root.py`: Removes root bone movement
- `export_fbx.py`: Exports armature/animation as FBX

**SOLID Principles**:
- **Single Responsibility**: Each use case is one feature
- **Dependency Inversion**: Depends on services, not implementation details

### 5. Adapters Layer (`adapters/blender/`)
**Purpose**: Blender framework integration

- **Framework-specific**: All Blender imports here
- **UI implementation**: Properties, Operators, Panels
- **Thin layer**: Delegates to use cases for business logic

**Files**:
- `properties.py`: Blender PropertyGroups (data storage)
- `operators.py`: Blender Operators (user actions)
- `panels.py`: Blender UI Panels (visual interface)
- `handlers.py`: Blender event handlers (depsgraph updates)

**SOLID Principles**:
- **Dependency Inversion**: Operators depend on use cases, not vice versa
- **Interface Segregation**: Separate concerns (properties, operators, UI)
- **Open/Closed**: Easy to add new operators without changing use cases

## Dependency Flow

```
┌─────────────────────────────────────────┐
│         Adapters (Blender UI)           │  ← Blender-specific
│  Properties, Operators, Panels, Handlers│
└────────────┬────────────────────────────┘
             │ depends on
             ▼
┌─────────────────────────────────────────┐
│          Use Cases (Business Rules)     │
│  Send to Timeline, Bake, Stabilize, Export│
└────────────┬────────────────────────────┘
             │ depends on
             ▼
┌─────────────────────────────────────────┐
│       Services (Action Manipulation)    │
│  FCurve operations, Action copying      │
└────────────┬────────────────────────────┘
             │ depends on
             ▼
┌─────────────────────────────────────────┐
│      Domain (Pure Business Logic)       │  ← Framework-independent
│  Entities, Math utilities               │
└─────────────────────────────────────────┘
             ▲
             │ used by
┌─────────────────────────────────────────┐
│       Config (Constants)                │
│  Defaults, Limits, Naming conventions   │
└─────────────────────────────────────────┘
```

**Key Rules**:
- **Inner layers never depend on outer layers**
- **Business logic is independent of Blender**
- **UI changes don't affect business logic**

## SOLID Principles Applied

### Single Responsibility Principle (SRP)
✅ **Before**: One 989-line file did everything
✅ **After**: Each module has one clear purpose

**Examples**:
- `math_utils.py`: Only mathematical operations
- `bake_animation.py`: Only NLA baking logic
- `operators.py`: Only Blender operator definitions

### Open/Closed Principle (OCP)
✅ **Extension without modification**

**Examples**:
- Add new use case: Create new file in `use_cases/`
- Add new operator: Add to `operators.py` without touching use cases
- Add new export format: Extend `export_fbx.py` without breaking existing

### Liskov Substitution Principle (LSP)
✅ **Compatible interfaces**

**Examples**:
- All use cases return `(success, message, data)` tuples
- All services accept standard Blender objects
- All operators follow Blender's execute/invoke pattern

### Interface Segregation Principle (ISP)
✅ **Small, focused interfaces**

**Examples**:
- Separate files for properties, operators, panels
- Focused functions: `rotate_2d_point()`, `stabilize_root_bone_axes()`
- Small data classes: `ActionItem`, `AnimationSettings`

### Dependency Inversion Principle (DIP)
✅ **Depend on abstractions, not concretions**

**Examples**:
- Operators depend on use cases (abstraction), not implementation
- Use cases depend on services (abstraction), not Blender details
- Domain layer has NO dependencies on Blender

## Benefits of Refactoring

### Maintainability
- **Clear structure**: Easy to find where functionality lives
- **Small files**: Each file < 200 lines (vs original 989 lines)
- **Focused modules**: Each module does one thing well

### Testability
- **Pure functions**: Domain and math utilities can be unit tested
- **Isolated logic**: Business rules separated from Blender
- **Mock-friendly**: Use cases return data, easy to test

### Extensibility
- **Add features**: New operators/use cases without touching existing code
- **Modify behavior**: Change use cases without updating UI
- **Replace parts**: Swap implementations without breaking others

### Readability
- **Self-documenting**: File names and structure explain purpose
- **Minimal coupling**: Changes don't cascade through codebase
- **Clear dependencies**: Import statements show relationships

## File Size Comparison

| Original | Refactored |
|----------|------------|
| `__init__.py` (989 lines) | Split into 19 focused modules |
| One monolithic file | Average 80 lines per file |
| Mixed concerns | Clear separation of concerns |

## Migration Notes

### Backwards Compatibility
✅ **Fully compatible** with existing `.blend` files

- Same `bl_info` metadata
- Same operator IDs (bl_idname)
- Same property names
- Same UI layout

### What Changed
- **Internal structure only**: User experience unchanged
- **Code organization**: From monolithic to modular
- **Dependency management**: Clear, explicit imports

### What Stayed the Same
- **Functionality**: All features work identically
- **UI**: Same panel, same buttons, same workflow
- **Data**: Same properties, same settings

## Development Workflow

### Adding New Feature
1. **Define domain entities** in `core/domain/entities.py` if needed
2. **Create service functions** in `core/services/` for logic
3. **Create use case** in `core/use_cases/` to orchestrate
4. **Create operator** in `adapters/blender/operators.py` for UI action
5. **Update panel** in `adapters/blender/panels.py` to expose feature

### Fixing Bug
1. **Identify layer**: Where does the bug occur?
   - Business logic → Use Cases
   - Calculation → Services or Domain
   - UI → Adapters
2. **Fix in isolation**: Change only affected layer
3. **Test independently**: No cascading changes needed

### Refactoring Code
- **Keep boundaries**: Don't mix layers
- **Follow dependency flow**: Inner layers never depend on outer
- **Maintain SOLID**: Single responsibility, clear interfaces

## Testing Strategy

### Unit Tests (Recommended)
- **Domain layer**: Test pure functions with standard Python unittest
- **Services layer**: Test with mock Blender objects
- **Use cases**: Test return values and state changes

### Integration Tests
- **Operators**: Test in Blender with test scenes
- **Full workflow**: Load → Send → Bake → Export

## Future Enhancements

Enabled by clean architecture:

1. **Plugin System**: Easy to add export formats (gLTF, Alembic)
2. **CLI Support**: Use cases can run without Blender UI
3. **Alternative UIs**: Create different panels using same use cases
4. **External Services**: Add cloud export, animation library integration
5. **Testing Suite**: Comprehensive unit and integration tests

## Summary

The refactoring transformed Mixanimo Lite from a **monolithic script** into a **professional, maintainable addon** following industry best practices:

- ✅ **Clean Architecture**: Clear separation of concerns
- ✅ **SOLID Principles**: Each component has one responsibility
- ✅ **Dependency Inversion**: Business logic independent of Blender
- ✅ **Testability**: Pure functions can be unit tested
- ✅ **Extensibility**: Easy to add features without breaking existing code
- ✅ **Readability**: Self-documenting structure and naming

**Result**: Same functionality, 10x better code organization.
