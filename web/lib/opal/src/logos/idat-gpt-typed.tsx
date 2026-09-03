import { cn } from "@opal/utils";

interface IdatGptTypedProps {
  size?: number;
  className?: string;
}

const DEFAULT_HEIGHT_PX = 24;
// Cap height of the wordmark relative to the mark height.
const HEIGHT_TO_FONT_RATIO = 0.72;

// "IDAT-GPT" wordmark, sized from the same height as the mark so both stay
// aligned. Inherits the theme text color unless a className overrides it.
const SvgIdatGptTyped = ({ size, className }: IdatGptTypedProps) => {
  const height = size ?? DEFAULT_HEIGHT_PX;

  return (
    <span
      className={cn("whitespace-nowrap select-none", className)}
      style={{
        fontSize: height * HEIGHT_TO_FONT_RATIO,
        lineHeight: 1,
        fontWeight: 700,
        letterSpacing: "-0.02em",
        color: "var(--theme-primary-05)",
      }}
    >
      IDAT-GPT
    </span>
  );
};
export default SvgIdatGptTyped;
