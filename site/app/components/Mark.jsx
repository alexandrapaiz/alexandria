// The library mark: ten sheared spines fanning around an empty center,
// pages of an open codex and a colonnade at once. The central hairline was
// removed on the owner's instruction, 2026-10-17; the animated hero mark
// (MarkLive) never had one. Vector recreation of
// Alexandra's reference so it stays crisp at wordmark scale.
export default function Mark(props) {
  const H = 900;
  const T = 60;
  const B = H - 60;
  // per side, outermost first: [width, shear]
  const spec = [
    [72, 170],
    [60, 140],
    [50, 110],
    [40, 80],
    [26, 50],
  ];
  const bars = [];
  for (let i = 0; i < 5; i++) {
    const [w, s] = spec[i];
    const cxL = 110 + i * 98;
    const cxR = 1090 - i * 98;
    // left group: caps slant down to the right
    bars.push(
      `${cxL - w / 2},${T} ${cxL + w / 2},${T + s} ${cxL + w / 2},${B} ${cxL - w / 2},${B - s}`
    );
    // right group: mirrored
    bars.push(
      `${cxR - w / 2},${T + s} ${cxR + w / 2},${T} ${cxR + w / 2},${B - s} ${cxR - w / 2},${B}`
    );
  }
  return (
    <svg
      viewBox="0 0 1200 900"
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
      {...props}
    >
      {bars.map((pts, i) => (
        <polygon key={i} points={pts} fill="currentColor" />
      ))}
    </svg>
  );
}
