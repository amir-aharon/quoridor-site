// utils/wallUtils.ts
import { WallState, Orientation } from './types';

// Function to get the walls to toggle on hover
export const getWallsToToggle = (
  wall: WallState,
  walls: WallState[]
): WallState[] => {
  let wallsToToggle: WallState[] = [];

  if (wall.occupied) return [];

  if (wall.orientation === Orientation.Horizontal) {
    // Add the horizontal wall itself
    wallsToToggle.push(wall);

    // Add the adjacent "None" wall and "Horizontal" wall to the left
    const leftNoneWall = walls.find(
      (w) =>
        w.row === wall.row &&
        w.col === wall.col - 1 &&
        w.orientation === Orientation.None
    );
    const leftHorizontalWall = walls.find(
      (w) =>
        w.row === wall.row &&
        w.col === wall.col - 1 &&
        w.orientation === Orientation.Horizontal
    );

    if (leftNoneWall && !leftNoneWall.occupied)
      wallsToToggle.push(leftNoneWall);
    if (leftHorizontalWall && !leftHorizontalWall.occupied)
      wallsToToggle.push(leftHorizontalWall);
  }

  if (wall.orientation === Orientation.Vertical) {
    // Add the vertical wall itself
    wallsToToggle.push(wall);

    // Add the adjacent "None" wall and "Vertical" wall above
    const belowNoneWall = walls.find(
      (w) =>
        w.row === wall.row &&
        w.col === wall.col &&
        w.orientation === Orientation.None
    );
    const belowVerticalWall = walls.find(
      (w) =>
        w.row === wall.row + 1 &&
        w.col === wall.col &&
        w.orientation === Orientation.Vertical
    );

    if (belowNoneWall && !belowNoneWall.occupied)
      wallsToToggle.push(belowNoneWall);
    if (belowVerticalWall && !belowVerticalWall.occupied)
      wallsToToggle.push(belowVerticalWall);
  }

  if (wallsToToggle.length < 3) {
    wallsToToggle = [];

    if (wall.orientation === Orientation.Horizontal) {
      // Add the horizontal wall itself
      wallsToToggle.push(wall);

      // Add the adjacent horizontal wall to the right
      const rightHorizontalWall = walls.find(
        (w) =>
          w.row === wall.row &&
          w.col === wall.col + 1 &&
          w.orientation === Orientation.Horizontal
      );
      const rightNoneWall = walls.find(
        (w) =>
          w.row === wall.row &&
          w.col === wall.col &&
          w.orientation === Orientation.None
      );

      if (rightNoneWall && !rightNoneWall.occupied)
        wallsToToggle.push(rightNoneWall);
      if (rightHorizontalWall && !rightHorizontalWall.occupied)
        wallsToToggle.push(rightHorizontalWall);
      else return []; // Ensure no walls are hovered if the pair is incomplete
    }

    if (wall.orientation === Orientation.Vertical) {
      // Add the vertical wall itself
      wallsToToggle.push(wall);

      // Add the adjacent "None" wall and "Vertical" wall above
      const aboveNoneWall = walls.find(
        (w) =>
          w.row === wall.row - 1 &&
          w.col === wall.col &&
          w.orientation === Orientation.None
      );
      const aboveVerticalWall = walls.find(
        (w) =>
          w.row === wall.row - 1 &&
          w.col === wall.col &&
          w.orientation === Orientation.Vertical
      );

      if (aboveNoneWall && !aboveNoneWall.occupied)
        wallsToToggle.push(aboveNoneWall);
      if (aboveVerticalWall && !aboveVerticalWall.occupied)
        wallsToToggle.push(aboveVerticalWall);
    }
  }

  if (wallsToToggle.length < 3) return [];

  return wallsToToggle;
};
