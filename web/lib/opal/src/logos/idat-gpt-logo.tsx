import type { IconProps } from "@opal/types";

// IDAT-GPT mark: a gradient tile with a neural "hub" (center node, eight
// connected nodes on a regular octagon of radius 19 around the center).
const SvgIdatGptLogo = ({ size, ...props }: IconProps) => (
  <svg
    height={size}
    width={size}
    viewBox="0 0 64 64"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <defs>
      <linearGradient
        id="idat-gpt-grad"
        x1="4"
        y1="4"
        x2="60"
        y2="60"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0" stopColor="#1D4ED8" />
        <stop offset="0.55" stopColor="#2563EB" />
        <stop offset="1" stopColor="#06B6D4" />
      </linearGradient>
    </defs>
    <rect
      x="2"
      y="2"
      width="60"
      height="60"
      rx="15"
      fill="url(#idat-gpt-grad)"
    />
    <path
      d="M32 13L45.4 18.6L51 32L45.4 45.4L32 51L18.6 45.4L13 32L18.6 18.6Z"
      stroke="#fff"
      strokeOpacity={0.45}
      strokeWidth={1.6}
      strokeLinejoin="round"
    />
    <g stroke="#fff" strokeLinecap="round">
      <path d="M32 32V13M32 32H51M32 32V51M32 32H13" strokeWidth={2} />
      <path
        d="M32 32L45.4 18.6M32 32L45.4 45.4M32 32L18.6 45.4M32 32L18.6 18.6"
        strokeOpacity={0.6}
        strokeWidth={1.6}
      />
    </g>
    <g fill="#fff">
      <circle cx="32" cy="13" r="3.4" />
      <circle cx="51" cy="32" r="3.4" />
      <circle cx="32" cy="51" r="3.4" />
      <circle cx="13" cy="32" r="3.4" />
      <circle cx="45.4" cy="18.6" r="2.4" fillOpacity={0.85} />
      <circle cx="45.4" cy="45.4" r="2.4" fillOpacity={0.85} />
      <circle cx="18.6" cy="45.4" r="2.4" fillOpacity={0.85} />
      <circle cx="18.6" cy="18.6" r="2.4" fillOpacity={0.85} />
    </g>
    <circle cx="32" cy="32" r="6.5" fill="#fff" />
    <circle cx="32" cy="32" r="3" fill="url(#idat-gpt-grad)" />
  </svg>
);
export default SvgIdatGptLogo;
