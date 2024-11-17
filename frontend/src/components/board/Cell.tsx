import { useState } from 'react';
import { CellState } from '../../utils/types';

interface CellProps {
  cell: CellState;
}

const Cell: React.FC<CellProps> = ({ cell }) => {
  const handleClick = () => {
    cell.selected = !cell.selected;
  };

  return (
    <div
      className={`cell ${
        cell.standingPlayer != null
          ? 'player-' + cell.standingPlayer.playerId
          : ''
      } ${cell.presentedOption ? 'presented-option' : ''}
      ${cell.selectable ? 'selectable' : ''}
      ${cell.selected ? 'selected' : ''}
      `} // Use wall.occupied here
      onClick={handleClick}
    >
      {cell.row}
      {cell.col}
    </div>
  );
};

export default Cell;
