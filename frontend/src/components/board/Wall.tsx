import React from 'react';
import { WallState } from '../../utils/types';

interface WallProps {
  wall: WallState;
  onHover: (
    row: number,
    col: number,
    orientation: WallState['orientation']
  ) => void;
  toggleOccupation: (
    row: number,
    col: number,
    orientation: WallState['orientation']
  ) => void;
}

const Wall: React.FC<WallProps> = ({ wall, onHover, toggleOccupation }) => {
  const handleHover = () => {
    onHover(wall.row, wall.col, wall.orientation);
  };

  const handleClick = () => {
    toggleOccupation(wall.row, wall.col, wall.orientation);
  };

  return (
    <div
      className={`wall wall-${wall.orientation} ${
        wall.selected ? 'hovered' : ''
      } ${wall.occupied ? 'occupied' : ''}`} // Use wall.occupied here
      onMouseEnter={handleHover}
      onMouseLeave={handleHover}
      onClick={handleClick}
    />
  );
};

export default Wall;
