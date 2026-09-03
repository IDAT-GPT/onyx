import SvgIdatGptLogo from "@opal/logos/idat-gpt-logo";
import SvgIdatGptTyped from "@opal/logos/idat-gpt-typed";
import { cn } from "@opal/utils";

interface IdatGptLogoTypedProps {
  size?: number;
  className?: string;
}

const HEIGHT_TO_GAP_RATIO = 5 / 16;

const SvgIdatGptLogoTyped = ({
  size: height,
  className,
}: IdatGptLogoTypedProps) => {
  const gap = height != null ? height * HEIGHT_TO_GAP_RATIO : undefined;

  return (
    <div
      className={cn("flex flex-row items-center", className)}
      style={{ gap }}
    >
      <SvgIdatGptLogo size={height} />
      <SvgIdatGptTyped size={height} />
    </div>
  );
};
export default SvgIdatGptLogoTyped;
