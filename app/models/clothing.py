from pydantic import BaseModel
from functools import total_ordering


@total_ordering
class Clothing(BaseModel):
    id: int
    name: str
    type: str
    category: str
    color: tuple[int, int, int]

    def __le__(self, other: "Clothing") -> bool:
        if self.category == "Top" and other.category == "Outerwear":
            return True

        if self.category == "Footwear" and other.category == "Socks":
            return True

        if self.category == other.category:
            return True

        return False

    def __repr__(self) -> str:
        return f"Clothing(id={self.id}, type='{self.type}', category='{self.category}')"


if __name__ == "__main__":
    c1 = Clothing(
        id=1, name="owl shirt", type="T-shirt", category="Top", color=(255, 0, 0)
    )
    c2 = Clothing(
        id=2,
        name="bomber jacket",
        type="Jacket",
        category="Outerwear",
        color=(0, 0, 255),
    )

    print(sorted([c2, c1]))  # Should print [c1, c2] since Top < Outerwear
