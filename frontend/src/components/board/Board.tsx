import React from 'react';
import Cell from './Cell';
import Wall from './Wall';
import '../../style/Board.css';
import { Orientation } from '../../utils/types';
import { useWalls } from '../../hooks/useWalls';
import { useWallInteractions } from '../../hooks/useWallInteractions';

const Board: React.FC = () => {
  const rows = [...Array(9).keys()];
  const columns = [...Array(9).keys()];

  const { walls, setWalls } = useWalls(9);
  const { handleWallHover, toggleOccupation } = useWallInteractions(
    walls,
    setWalls
  );

  const [cells, setCells] = useState<CellState[]>(9);

  const generateWall = (row: number, col: number, orientation: Orientation) => {
    const wall = walls.find(
      (w) => w.row === row && w.col === col && w.orientation === orientation
    );

    if (!wall) return null;
    return (
      <Wall
        wall={wall}
        onHover={() => handleWallHover(wall)}
        toggleOccupation={toggleOccupation}
      />
    );
  };

  const generateCell = (row: number, col: number) => {
    const cell = {
      row,
      col,
      standingPlayer: null,
      presentedOption: false,
      selected: false,
      selectable: true,
    };

    if (!cell) return null;
    return <Cell cell={cell} />;
  };

  return (
    <div className="board">
      {rows.map((row) => (
        <React.Fragment key={`row-${row}`}>
          {columns.map((col) => (
            <React.Fragment key={`vertical-${row}-${col}`}>
              {generateCell(row, col)}
              {col !== columns.length - 1 &&
                generateWall(row, col, Orientation.Vertical)}
            </React.Fragment>
          ))}
          {row !== rows.length - 1 &&
            columns.map((col) => (
              <React.Fragment key={`horizontal-${row}-${col}`}>
                {generateWall(row, col, Orientation.Horizontal)}
                {col !== columns.length - 1 &&
                  generateWall(row, col, Orientation.None)}
              </React.Fragment>
            ))}
        </React.Fragment>
      ))}
    </div>
  );
};

export default Board;
