// hooks/useWalls.ts
import { useState } from 'react';
import { Orientation, WallState } from '../utils/types';

export const useWalls = (boardSize: number) => {
  const [walls, setWalls] = useState<WallState[]>(() => {
    const initialWalls: WallState[] = [];
    [...Array(boardSize).keys()].forEach((row) => {
      [...Array(boardSize).keys()].forEach((col) => {
        initialWalls.push(
          {
            row,
            col,
            orientation: Orientation.Horizontal,
            selected: false,
            occupied: false,
          },
          {
            row,
            col,
            orientation: Orientation.Vertical,
            selected: false,
            occupied: false,
          },
          {
            row,
            col,
            orientation: Orientation.None,
            selected: false,
            occupied: false,
          }
        );
      });
    });
    return initialWalls;
  });

  return { walls, setWalls };
};
