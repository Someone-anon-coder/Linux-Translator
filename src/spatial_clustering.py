def cluster_bboxes(bboxes, x_threshold=20, y_threshold=10):
    """
    Merges boxes that are physically close to each other.
    """
    if not bboxes:
        return []

    # Sort boxes by top-to-bottom (Y) then left-to-right (X)
    bboxes.sort(key=lambda b: (b[1], b[0]))

    clusters = []
    if bboxes:
        current_cluster = bboxes[0]

        for i in range(1, len(bboxes)):
            prev = current_cluster
            curr = bboxes[i]

            # Check if boxes are on the same line and close horizontally
            same_row = abs(curr[1] - prev[1]) < y_threshold
            close_horizontally = (curr[0] - prev[2]) < x_threshold

            if same_row and close_horizontally:
                # Merge: Extend the current cluster box
                new_x1 = min(prev[0], curr[0])
                new_y1 = min(prev[1], curr[1])
                new_x2 = max(prev[2], curr[2])
                new_y2 = max(prev[3], curr[3])
                current_cluster = [new_x1, new_y1, new_x2, new_y2]
            else:
                clusters.append(current_cluster)
                current_cluster = curr
        
        clusters.append(current_cluster)
    
    return clusters

if __name__ == "__main__":
    print("--- Spatial Clustering Test ---")
    # Simulated boxes: [x1, y1, x2, y2]
    # These represent two words close to each other
    mock_boxes = [[10, 10, 50, 30], [60, 10, 100, 30], [10, 50, 80, 70]]
    print(f"Original Box Count: {len(mock_boxes)}")
    
    merged = cluster_bboxes(mock_boxes)
    print(f"Merged Box Count: {len(merged)}")
    print(f"Merged Result: {merged}")
    print("--- Test Finished ---")