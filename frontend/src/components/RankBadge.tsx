interface Props {
  rank: number
  badgeLevel: number
}

function decodeBadgeLevel(badgeLevel: number) {
  const tier = Math.floor(badgeLevel / 10)
  const subrank = badgeLevel % 10
  return { tier, subrank }
}

function getRankFolder(tier: number): string {
  const map: Record<number, string> = {
    0: "0_obscurus",
    1: "1_initiate",
    2: "2_seeker",
    3: "3_alchemist",
    4: "4_arcanist",
    5: "5_ritualist",
    6: "6_emissary",
    7: "7_archon",
    8: "8_oracle",
    9: "9_phantom",
    10: "10_ascendant",
    11: "11_eternus",
  }

  return map[tier] ?? "0_obscurus"
}

export default function RankBadge({ rank, badgeLevel }: Props) {
  const { tier, subrank } = decodeBadgeLevel(badgeLevel)
  const folder = getRankFolder(tier)

  const imgSrc =
    subrank > 0
      ? `/ranks_webp/${folder}/badge_lg_subrank${subrank}.webp`
      : `/ranks_webp/${folder}/badge_lg.webp`

  return (
    <div className="flex items-center gap-2">
      <span className={`text-sm font-mono font-bold w-8 text-center`}>
        #{rank}
      </span>

      <img
        src={imgSrc}
        className="w-8 h-8 object-contain"
        alt={`Tier ${tier} Subrank ${subrank}`}
      />
    </div>
  )
}