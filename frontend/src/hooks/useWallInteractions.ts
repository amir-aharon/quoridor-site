// hooks/useWallInteractions.ts
import { WallState } from '../utils/types';
import { getWallsToToggle } from '../utils/wallUtils';

export const useWallInteractions = (
  walls: WallState[],
  setWalls: React.Dispatch<React.SetStateAction<WallState[]>>
) => {
  const handleWallHover = (wall: WallState) => {
    const wallsToToggle = getWallsToToggle(wall, walls);
    setWalls((prevWalls) =>
      prevWalls.map((w) =>
        wallsToToggle.some(
          (toggledWall) =>
            toggledWall.row === w.row &&
            toggledWall.col === w.col &&
            toggledWall.orientation === w.orientation
        )
          ? { ...w, selected: !w.selected }
          : w
      )
    );
  };

  const toggleOccupation = () => {
    setWalls((prevWalls) =>
      prevWalls.map((wall) =>
        wall.selected ? { ...wall, occupied: true } : wall
      )
    );
  };

  return { handleWallHover, toggleOccupation };
};
