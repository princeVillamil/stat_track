import React from 'react';

const avgELO = {
  Initiate: {
    1: { elo: 25,  img: "/ranks_webp/initiate/large_subrank1.webp" },
    2: { elo: 50,  img: "/ranks_webp/initiate/large_subrank2.webp" },
    3: { elo: 75,  img: "/ranks_webp/initiate/large_subrank3.webp" },
    4: { elo: 100, img: "/ranks_webp/initiate/large_subrank4.webp" },
    5: { elo: 125, img: "/ranks_webp/initiate/large_subrank5.webp" },
    6: { elo: 150, img: "/ranks_webp/initiate/large_subrank6.webp" },
  },
  Seeker: {
    1: { elo: 175, img: "/ranks_webp/seeker/large_subrank1.webp" },
    2: { elo: 200, img: "/ranks_webp/seeker/large_subrank2.webp" },
    3: { elo: 225, img: "/ranks_webp/seeker/large_subrank3.webp" },
    4: { elo: 250, img: "/ranks_webp/seeker/large_subrank4.webp" },
    5: { elo: 275, img: "/ranks_webp/seeker/large_subrank5.webp" },
    6: { elo: 300, img: "/ranks_webp/seeker/large_subrank6.webp" },
  },
  Alchemist: {
    1: { elo: 325, img: "/ranks_webp/alchemist/large_subrank1.webp" },
    2: { elo: 350, img: "/ranks_webp/alchemist/large_subrank2.webp" },
    3: { elo: 375, img: "/ranks_webp/alchemist/large_subrank3.webp" },
    4: { elo: 400, img: "/ranks_webp/alchemist/large_subrank4.webp" },
    5: { elo: 425, img: "/ranks_webp/alchemist/large_subrank5.webp" },
    6: { elo: 450, img: "/ranks_webp/alchemist/large_subrank6.webp" },
  },
  Arcanist: {
    1: { elo: 475, img: "/ranks_webp/arcanist/large_subrank1.webp" },
    2: { elo: 500, img: "/ranks_webp/arcanist/large_subrank2.webp" },
    3: { elo: 525, img: "/ranks_webp/arcanist/large_subrank3.webp" },
    4: { elo: 550, img: "/ranks_webp/arcanist/large_subrank4.webp" },
    5: { elo: 575, img: "/ranks_webp/arcanist/large_subrank5.webp" },
    6: { elo: 600, img: "/ranks_webp/arcanist/large_subrank6.webp" },
  },
  Ritualist: {
    1: { elo: 625, img: "/ranks_webp/ritualist/large_subrank1.webp" },
    2: { elo: 650, img: "/ranks_webp/ritualist/large_subrank2.webp" },
    3: { elo: 675, img: "/ranks_webp/ritualist/large_subrank3.webp" },
    4: { elo: 700, img: "/ranks_webp/ritualist/large_subrank4.webp" },
    5: { elo: 725, img: "/ranks_webp/ritualist/large_subrank5.webp" },
    6: { elo: 750, img: "/ranks_webp/ritualist/large_subrank6.webp" },
  },
  Emissary: {
    1: { elo: 775, img: "/ranks_webp/emissary/large_subrank1.webp" },
    2: { elo: 800, img: "/ranks_webp/emissary/large_subrank2.webp" },
    3: { elo: 825, img: "/ranks_webp/emissary/large_subrank3.webp" },
    4: { elo: 850, img: "/ranks_webp/emissary/large_subrank4.webp" },
    5: { elo: 875, img: "/ranks_webp/emissary/large_subrank5.webp" },
    6: { elo: 900, img: "/ranks_webp/emissary/large_subrank6.webp" },
  },
  Archon: {
    1: { elo: 925, img: "/ranks_webp/archon/large_subrank1.webp" },
    2: { elo: 950, img: "/ranks_webp/archon/large_subrank2.webp" },
    3: { elo: 975, img: "/ranks_webp/archon/large_subrank3.webp" },
    4: { elo: 1000, img: "/ranks_webp/archon/large_subrank4.webp" },
    5: { elo: 1025, img: "/ranks_webp/archon/large_subrank5.webp" },
    6: { elo: 1050, img: "/ranks_webp/archon/large_subrank6.webp" },
  },
  Oracle: {
    1: { elo: 1075, img: "/ranks_webp/oracle/large_subrank1.webp" },
    2: { elo: 1100, img: "/ranks_webp/oracle/large_subrank2.webp" },
    3: { elo: 1125, img: "/ranks_webp/oracle/large_subrank3.webp" },
    4: { elo: 1150, img: "/ranks_webp/oracle/large_subrank4.webp" },
    5: { elo: 1175, img: "/ranks_webp/oracle/large_subrank5.webp" },
    6: { elo: 1200, img: "/ranks_webp/oracle/large_subrank6.webp" },
  },
  Phantom: {
    1: { elo: 1225, img: "/ranks_webp/phantom/large_subrank1.webp" },
    2: { elo: 1250, img: "/ranks_webp/phantom/large_subrank2.webp" },
    3: { elo: 1275, img: "/ranks_webp/phantom/large_subrank3.webp" },
    4: { elo: 1300, img: "/ranks_webp/phantom/large_subrank4.webp" },
    5: { elo: 1325, img: "/ranks_webp/phantom/large_subrank5.webp" },
    6: { elo: 1350, img: "/ranks_webp/phantom/large_subrank6.webp" },
  },
  Ascendant: {
    1: { elo: 1375, img: "/ranks_webp/ascendant/large_subrank1.webp" },
    2: { elo: 1400, img: "/ranks_webp/ascendant/large_subrank2.webp" },
    3: { elo: 1425, img: "/ranks_webp/ascendant/large_subrank3.webp" },
    4: { elo: 1450, img: "/ranks_webp/ascendant/large_subrank4.webp" },
    5: { elo: 1475, img: "/ranks_webp/ascendant/large_subrank5.webp" },
    6: { elo: 1500, img: "/ranks_webp/ascendant/large_subrank6.webp" },
  },
  Eternus: {
    1: { elo: 1525, img: "/ranks_webp/eternus/large_subrank1.webp" },
    2: { elo: 1550, img: "/ranks_webp/eternus/large_subrank2.webp" },
    3: { elo: 1575, img: "/ranks_webp/eternus/large_subrank3.webp" },
    4: { elo: 1600, img: "/ranks_webp/eternus/large_subrank4.webp" },
    5: { elo: 1625, img: "/ranks_webp/eternus/large_subrank5.webp" },
    6: { elo: "1650+", img: "/ranks_webp/eternus/large_subrank6.webp" },
  },
} as const;

const RANKS = [
  { name: 'Initiate', color: '#708090' },
  { name: 'Seeker', color: '#CD7F32' },
  { name: 'Alchemist', color: '#C0C0C0' },
  { name: 'Arcanist', color: '#FFD700' },
  { name: 'Ritualist', color: '#2ECC71' },
  { name: 'Emissary', color: '#00CED1' },
  { name: 'Archon', color: '#4169E1' },
  { name: 'Oracle', color: '#9B59B6' },
  { name: 'Phantom', color: '#FF00FF' },
  { name: 'Ascendant', color: '#E74C3C' },
  { name: 'Eternus', color: '#FDFEFE' },
];

const SUBRANK_LABELS: Record<number, string> = {
  6: "✪",
  5: "V",
  4: "IV",
  3: "III",
  2: "II",
  1: "I",
};

export const RankDistributionChart: React.FC = () => {
  const k = 0.048; // Decay constant for smooth 100% -> 5% curve

  return (
    <div className="w-full mb-12">
      <div className="bg-slate-900/50 border border-slate-800 rounded-sm p-6 md:p-10 shadow-2xl backdrop-blur-sm">
        <div className="mb-16">
          <h2 className="text-slate-400 text-[10px] md:text-xs font-bold tracking-[0.4em] uppercase opacity-80">
            ELO PER RANKED MEDAL DISTRIBUTION
          </h2>
        </div>

        <div className="flex items-end justify-between gap-[1px] md:gap-[2px] h-80 mb-6">
          {RANKS.map((rank, rankIdx) => (
            <div key={rank.name} className="flex flex-1 items-end gap-[1px] md:gap-[2px] h-full">
              {[6, 5, 4, 3, 2, 1].map((subrank, subIdx) => {
                // Global index for the exponential curve (0 to 65)
                const globalIndex = rankIdx * 6 + subIdx;
                const heightPercent = 100 * Math.exp(-k * globalIndex);
                const data = avgELO[rank.name as keyof typeof avgELO][subrank as 1|2|3|4|5|6];

                return (
                  <div 
                    key={`${rank.name}-${subrank}`} 
                    className="flex flex-col items-center group relative flex-1"
                    style={{ height: '100%' }}
                  >
                    {/* Rank Badge Image */}
                    <div className="absolute -top-10 w-6 h-6 md:w-8 md:h-8 flex items-center justify-center transition-transform duration-300 group-hover:-translate-y-1">
                      <img 
                        src={data.img} 
                        alt={`${rank.name} ${subrank}`}
                        className="w-full h-full object-contain filter drop-shadow-[0_0_3px_rgba(0,0,0,0.5)]"
                        onError={(e) => (e.currentTarget.style.display = 'none')}
                      />
                    </div>

                    {/* ELO Tooltip (Visible on Hover) */}
                    <div className="absolute -top-16 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-20 pointer-events-none">
                       <div className="bg-slate-800 border border-slate-700 px-2 py-1 rounded shadow-xl whitespace-nowrap text-[9px] text-white font-mono">
                         {data.elo} <span className="text-slate-400 ml-1">ELO</span>
                       </div>
                    </div>
                    
                    {/* The Bar */}
                    <div className="flex flex-col justify-end w-full h-full pt-12">
                       <div 
                        className="w-full transition-all duration-500 group-hover:brightness-150 group-hover:scale-x-110 origin-bottom"
                        style={{ 
                          height: `${heightPercent}%`, 
                          backgroundColor: rank.color,
                          boxShadow: `0 0 15px ${rank.color}22`
                        }}
                      />
                    </div>

                    {/* Subrank Label */}
                    <div className="mt-3 w-full px-[1px]">
                      <div className="bg-slate-950/50 border border-slate-800 text-[7px] md:text-[9px] text-white font-medium w-full py-0.5 text-center rounded-[1px] group-hover:bg-slate-800 transition-colors">
                        {SUBRANK_LABELS[subrank]}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>

        {/* Legend / Rank Names */}
        <div className="grid grid-cols-11 gap-1 mt-10 border-t border-slate-800/50 pt-6">
          {RANKS.map((rank) => (
            <div key={rank.name} className="flex flex-col items-center">
              <img
                src={`/ranks_webp/${RANKS.indexOf(rank)+1}_${rank.name.toLowerCase()}/badge_lg_subrank6.webp`}
                alt={rank.name}
                className="w-10 h-10 mb-2 object-contain"
              />
              <span 
                className="text-[7px] md:text-[8px] font-bold uppercase tracking-[0.15em] text-center"
                style={{ color: rank.color }}
              >
                {rank.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RankDistributionChart;
