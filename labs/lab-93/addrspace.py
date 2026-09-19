"""
Lab 93: Assemble the Address Space

Glue a device's separate images into one address space, and measure what
that alone does to the unresolved-transfer count.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class Overlap(Exception):
    """Raised when two images would occupy the same addresses."""


class AddressSpace:
    """Several images mapped into one flat space."""

    def __init__(self):
        self.images = []        # list of (base, size, name)

    def add(self, name, base, size):
        """Map an image.

        Raises:
            Overlap: if it would collide with one already mapped. Silently
                allowing an overlap means every later lookup is a coin flip.
        """
        # TODO: Check every existing image for an overlapping range, then
        #       append and keep self.images sorted by base.
        pass

    def contains(self, addr):
        """Is *addr* inside any mapped image?"""
        # TODO: Any image whose range covers addr.
        pass

    def image_of(self, addr):
        """Which image owns *addr*?

        Returns:
            The image name, or None.
        """
        # TODO: Return the name of the covering image.
        pass


def analyse(transfers, space):
    """Classify transfer targets against an address space.

    Args:
        transfers: list of dicts with "site" and "target" addresses.
        space: an AddressSpace.

    Returns:
        A dict with:
            "total"      - how many transfers
            "resolved"   - targets inside the space
            "unresolved" - targets outside it
            "outside"    - sorted list of the unresolved target addresses
    """
    # TODO: Count each transfer by whether the space contains its target.
    pass


def compare_assembly(images, transfers):
    """Compare analysing each image alone against analysing them together.

    Args:
        images: list of (name, base, size) tuples.
        transfers: list of transfer dicts.

    Returns:
        A dict with:
            "separate"   - unresolved count when each image is analysed alone
            "combined"   - unresolved count with everything mapped together
            "recovered"  - separate - combined
            "ratio"      - combined / separate, 0.0 when separate is 0

    Analysing "alone" means: for each image, build a space containing only that
    image, and count the transfers whose *site* is in that image but whose
    target is not.
    """
    # TODO: Build the per-image spaces and the combined space, and count.
    pass
