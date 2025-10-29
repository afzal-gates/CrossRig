"""
Use case for automatic bone mapping using fuzzy name matching.

Implements intelligent bone name matching using multiple strategies:
- Exact match
- Case-insensitive match
- Prefix/suffix removal
- String similarity scoring
"""

from typing import List, Tuple, Dict, Optional
import re

from ..domain.bone_mapping_entities import BoneMappingPreset, BoneMapping


def normalize_bone_name(bone_name: str) -> str:
    """
    Normalize bone name for comparison.

    Removes common prefixes, normalizes case, and cleans up separators.

    Args:
        bone_name: Original bone name

    Returns:
        str: Normalized bone name
    """
    # Convert to lowercase
    name = bone_name.lower()

    # Remove common prefixes
    prefixes = [
        'mixamorig:',
        'def-',
        'mch-',
        'org-',
        'ctrl-',
        'ik-',
        'fk-',
        'root.',
        'rig.',
    ]

    for prefix in prefixes:
        if name.startswith(prefix.lower()):
            name = name[len(prefix):]
            break

    # Normalize separators (convert all to underscore)
    name = re.sub(r'[-:. ]', '_', name)

    # Remove duplicate underscores
    name = re.sub(r'_+', '_', name)

    # Strip leading/trailing underscores
    name = name.strip('_')

    return name


def normalize_side_suffix(bone_name: str) -> Tuple[str, str]:
    """
    Extract and normalize side suffix (left/right) from bone name.

    Args:
        bone_name: Bone name to analyze

    Returns:
        Tuple[str, str]: (base_name, side) where side is 'L', 'R', or ''
    """
    name = bone_name.lower()

    # Common left patterns
    left_patterns = [
        r'[._-]l$',      # .L, _L, -L
        r'[._-]left$',   # .left, _left, -left
        r'^l[._-]',      # L., L_, L-
        r'^left[._-]',   # left., left_, left-
    ]

    # Common right patterns
    right_patterns = [
        r'[._-]r$',      # .R, _R, -R
        r'[._-]right$',  # .right, _right, -right
        r'^r[._-]',      # R., R_, R-
        r'^right[._-]',  # right., right_, right-
    ]

    # Check for left side
    for pattern in left_patterns:
        if re.search(pattern, name):
            base = re.sub(pattern, '', name)
            return (base, 'L')

    # Check for right side
    for pattern in right_patterns:
        if re.search(pattern, name):
            base = re.sub(pattern, '', name)
            return (base, 'R')

    return (name, '')


def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity score between two strings using Levenshtein distance.

    Args:
        str1: First string
        str2: Second string

    Returns:
        float: Similarity score (0.0 to 1.0)
    """
    if str1 == str2:
        return 1.0

    if not str1 or not str2:
        return 0.0

    # Levenshtein distance implementation
    len1, len2 = len(str1), len(str2)

    # Create distance matrix
    matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    # Initialize first row and column
    for i in range(len1 + 1):
        matrix[i][0] = i
    for j in range(len2 + 1):
        matrix[0][j] = j

    # Calculate distances
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if str1[i-1] == str2[j-1]:
                cost = 0
            else:
                cost = 1

            matrix[i][j] = min(
                matrix[i-1][j] + 1,      # deletion
                matrix[i][j-1] + 1,      # insertion
                matrix[i-1][j-1] + cost  # substitution
            )

    # Calculate similarity (0.0 to 1.0)
    max_len = max(len1, len2)
    distance = matrix[len1][len2]
    similarity = 1.0 - (distance / max_len)

    return similarity


def find_best_match(
    source_bone: str,
    target_bones: List[str],
    threshold: float = 0.6
) -> Tuple[Optional[str], float]:
    """
    Find best matching target bone for a source bone.

    Uses multiple matching strategies with confidence scoring.

    Args:
        source_bone: Source bone name
        target_bones: List of available target bone names
        threshold: Minimum confidence threshold (0.0-1.0)

    Returns:
        Tuple[Optional[str], float]: (best_match, confidence)
    """
    if not target_bones:
        return (None, 0.0)

    best_match = None
    best_confidence = 0.0

    # Strategy 1: Exact match (confidence: 1.0)
    if source_bone in target_bones:
        return (source_bone, 1.0)

    # Strategy 2: Case-insensitive exact match (confidence: 0.95)
    source_lower = source_bone.lower()
    for target in target_bones:
        if target.lower() == source_lower:
            return (target, 0.95)

    # Strategy 3: Normalized name match (confidence: 0.9)
    source_normalized = normalize_bone_name(source_bone)
    source_base, source_side = normalize_side_suffix(source_normalized)

    for target in target_bones:
        target_normalized = normalize_bone_name(target)
        target_base, target_side = normalize_side_suffix(target_normalized)

        # Check if base names match and sides match (or no side)
        if source_base == target_base:
            if source_side == target_side or not source_side or not target_side:
                confidence = 0.9
                if confidence > best_confidence:
                    best_match = target
                    best_confidence = confidence

    # Strategy 4: Similarity scoring (confidence: 0.6-0.85)
    if best_confidence < 0.9:
        for target in target_bones:
            target_normalized = normalize_bone_name(target)

            # Compare normalized names
            similarity = calculate_similarity(source_normalized, target_normalized)

            # Check side consistency
            target_base, target_side = normalize_side_suffix(target_normalized)
            if source_side and target_side and source_side != target_side:
                # Penalize opposite sides
                similarity *= 0.5

            # Scale similarity to confidence range 0.6-0.85
            confidence = 0.6 + (similarity * 0.25)

            if confidence > best_confidence:
                best_match = target
                best_confidence = confidence

    # Return best match if above threshold
    if best_confidence >= threshold:
        return (best_match, best_confidence)

    return (None, 0.0)


def auto_map_bones(
    mapping_preset: BoneMappingPreset,
    source_bones: List[str],
    target_bones: List[str],
    threshold: float = 0.6,
    preserve_existing: bool = True
) -> Tuple[bool, str, BoneMappingPreset]:
    """
    Automatically map bones using fuzzy matching.

    Args:
        mapping_preset: BoneMappingPreset to populate
        source_bones: List of source bone names
        target_bones: List of target bone names
        threshold: Minimum confidence threshold (0.0-1.0)
        preserve_existing: Keep existing manual mappings

    Returns:
        Tuple[bool, str, BoneMappingPreset]: (success, message, updated_preset)
    """
    try:
        # Track already mapped target bones to avoid duplicates
        used_targets = set()

        # Preserve existing mappings if requested
        if preserve_existing:
            for mapping in mapping_preset.mappings:
                if mapping.confidence >= 1.0:  # Manual or exact matches
                    used_targets.add(mapping.target_bone)

        # Available target bones
        available_targets = [b for b in target_bones if b not in used_targets]

        # Auto-map each source bone
        mapped_count = 0
        skipped_count = 0

        for source_bone in source_bones:
            # Skip if already mapped (and preserving)
            if preserve_existing and mapping_preset.find_target_bone(source_bone):
                skipped_count += 1
                continue

            # Find best match
            best_match, confidence = find_best_match(
                source_bone,
                available_targets,
                threshold
            )

            if best_match:
                # Add mapping
                mapping_preset.add_mapping(source_bone, best_match, confidence)
                used_targets.add(best_match)
                available_targets.remove(best_match)
                mapped_count += 1

        # Update metadata
        mapping_preset.update_metadata()

        message = (
            f"Auto-mapping complete:\n"
            f"Mapped: {mapped_count} bones\n"
            f"Skipped: {skipped_count} bones (already mapped)\n"
            f"Unmapped: {len(source_bones) - mapped_count - skipped_count} bones\n"
            f"Total mappings: {mapping_preset.mapped_count}"
        )

        return (True, message, mapping_preset)

    except Exception as e:
        return (False, f"Auto-mapping failed: {str(e)}", mapping_preset)


def suggest_mapping(
    source_bone: str,
    target_bones: List[str],
    threshold: float = 0.6
) -> List[Tuple[str, float]]:
    """
    Suggest multiple possible mappings for a source bone.

    Returns top 5 matches sorted by confidence.

    Args:
        source_bone: Source bone name
        target_bones: List of available target bone names
        threshold: Minimum confidence threshold

    Returns:
        List[Tuple[str, float]]: List of (target_bone, confidence) sorted by confidence
    """
    suggestions = []

    source_normalized = normalize_bone_name(source_bone)
    source_base, source_side = normalize_side_suffix(source_normalized)

    for target in target_bones:
        target_normalized = normalize_bone_name(target)
        target_base, target_side = normalize_side_suffix(target_normalized)

        # Calculate similarity
        similarity = calculate_similarity(source_normalized, target_normalized)

        # Check side consistency
        if source_side and target_side and source_side != target_side:
            similarity *= 0.5

        # Convert to confidence
        confidence = 0.6 + (similarity * 0.4)

        if confidence >= threshold:
            suggestions.append((target, confidence))

    # Sort by confidence (highest first)
    suggestions.sort(key=lambda x: x[1], reverse=True)

    # Return top 5
    return suggestions[:5]
