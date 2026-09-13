// Shelf art for the library page: rows of book spines, a few leaning, a few
// lying flat. Vector recreation of Alexandra's reference, hand-placed row by
// row so the composition is deliberate, not random.

const PITCH = 22; // spine-to-spine distance
const W = 9; // stroke width
const BOOK = 150; // spine height
const ROWGAP = 70;

// tokens: v = n upright spines, lean = one leaning spine (deg, + leans left),
// gap = empty shelf space, h = n stacked flat books of width w,
// fallen = one shallow diagonal resting on two flat books
const ROWS = [
  [["v", 17], ["gap", 30], ["lean", -12], ["lean", -10], ["v", 34]],
  [["v", 26], ["gap", 40], ["v", 14], ["gap", 30], ["h", 3, 220]],
  [["v", 6], ["h", 6, 200], ["v", 39]],
  [["v", 2], ["lean", 14], ["v", 40], ["gap", 30], ["lean", -14], ["v", 6]],
  [["v", 14], ["lean", 16], ["gap", 10], ["fallen", 220], ["v", 29]],
];

function buildShapes() {
  const shapes = [];
  ROWS.forEach((row, r) => {
    const yTop = r * (BOOK + ROWGAP);
    const yBot = yTop + BOOK;
    let x = 0;
    for (const [t, a, b] of row) {
      if (t === "v") {
        for (let i = 0; i < a; i++) {
          shapes.push(["line", x + W / 2, yBot, x + W / 2, yTop]);
          x += PITCH;
        }
      } else if (t === "gap") {
        x += a;
      } else if (t === "lean") {
        const dx = Math.tan((Math.abs(a) * Math.PI) / 180) * BOOK * Math.sign(a);
        shapes.push(["line", x + W / 2 + Math.max(dx, 0), yBot, x + W / 2 + Math.max(-dx, 0), yTop]);
        x += PITCH + Math.abs(dx);
      } else if (t === "h") {
        for (let i = 0; i < a; i++) {
          const y = yBot - W / 2 - i * (W + 9);
          shapes.push(["line", x, y, x + b, y]);
        }
        x += b + PITCH;
      } else if (t === "fallen") {
        shapes.push(["line", x, yBot - W / 2, x + a, yBot - W / 2]);
        shapes.push(["line", x, yBot - W / 2 - 18, x + a, yBot - W / 2 - 18]);
        shapes.push(["line", x + 10, yBot - 40, x + a - 15, yBot - 105]);
        x += a + PITCH;
      }
    }
  });
  return shapes;
}

export default function Shelves(props) {
  const height = ROWS.length * (BOOK + ROWGAP) - ROWGAP;
  return (
    <svg
      viewBox={`0 0 1240 ${height}`}
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
      {...props}
    >
      {buildShapes().map(([, x1, y1, x2, y2], i) => (
        <line
          key={i}
          x1={x1}
          y1={y1}
          x2={x2}
          y2={y2}
          stroke="currentColor"
          strokeWidth={W}
        />
      ))}
    </svg>
  );
}
