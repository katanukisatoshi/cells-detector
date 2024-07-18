class IntersectionFinder:
    @staticmethod
    def find_intersections(horizontal_lines, vertical_lines):
        intersections = []
        for y in horizontal_lines:
            for x in vertical_lines:
                intersections.append((x, y))
        return intersections
