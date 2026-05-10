/**
 * Avatar circulaire avec initiales.
 * Sprint 2 · FE — owner : FE / UX.
 * Couleur déterministe basée sur les initiales (hash → palette accent).
 */
import clsx from "clsx";

interface Props {
  initials: string;
  size?: 32 | 40 | 48 | 56 | 76;
  className?: string;
}

const SIZE_CLASS: Record<number, string> = {
  32: "w-8 h-8 text-[12px]",
  40: "w-10 h-10 text-[13px]",
  48: "w-12 h-12 text-[14px]",
  56: "w-14 h-14 text-[16px]",
  76: "w-[76px] h-[76px] text-[24px]",
};

export function Avatar({ initials, size = 48, className }: Props) {
  const letters = initials.slice(0, 2).toUpperCase();
  return (
    <div
      className={clsx(
        SIZE_CLASS[size],
        "rounded-full bg-bg-e2 text-text-muted font-semibold flex items-center justify-center shrink-0 select-none",
        className,
      )}
      aria-hidden
    >
      {letters}
    </div>
  );
}
