import React from 'react';

// Static Hero List derived from src/assets/heroes.json (filtered for player_selectable: true)
const HEROES = [
  { name: "Infernus", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/inferno_card.png" },
  { name: "Seven", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/gigawatt_card.png" },
  { name: "Vindicta", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/hornet_card.png" },
  { name: "Lady Geist", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/spectre_card.png" },
  { name: "Abrams", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/bull_card.png" },
  { name: "Wraith", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/wraith_card.png" },
  { name: "McGinnis", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/engineer_card.png" },
  { name: "Paradox", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/chrono_card.png" },
  { name: "Dynamo", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/sumo_card.png" },
  { name: "Kelvin", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/kelvin_card.png" },
  { name: "Haze", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/haze_card.png" },
  { name: "Holliday", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/astro_card.png" },
  { name: "Bebop", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/bebop_card.png" },
  { name: "Calico", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/nano_card.png" },
  { name: "Grey Talon", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/archer_card.png" },
  { name: "Mo & Krill", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/digger_card.png" },
  { name: "Shiv", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/shiv_card.png" },
  { name: "Ivy", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/tengu_card.png" },
  { name: "Warden", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/warden_card.png" },
  { name: "Yamato", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/yamato_card.png" },
  { name: "Lash", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/lash_card.png" },
  { name: "Viscous", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/viscous_card.png" },
  { name: "Pocket", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/synth_card.png" },
  { name: "Mirage", icon: "https://assets-bucket.deadlock-api.com/assets-api-res/images/heroes/mirage_card.png" },
].sort((a, b) => a.name.localeCompare(b.name));

export const HeroList: React.FC = () => {
  return (
    <div className="w-64 flex-shrink-0 flex flex-col h-fit bg-slate-900/50 border border-slate-800 rounded-sm shadow-2xl backdrop-blur-sm overflow-hidden">
      {/* Header - Matching Chart Title Style */}
      <div className="px-6 py-5 border-b border-slate-800/50">
        <h2 className="text-slate-400 text-[10px] font-bold tracking-[0.4em] uppercase opacity-80">
          Heroes
        </h2>
      </div>

      {/* Hero List Container */}
      <div className="flex flex-col max-h-[720px] overflow-y-auto custom-scrollbar">
        {HEROES.map((hero, index) => (
          <div 
            key={hero.name}
            className={`
              px-6 py-3.5 flex items-center gap-4 border-b border-slate-800/30 
              transition-all duration-300 cursor-default group
              ${index % 2 === 0 ? 'bg-transparent' : 'bg-slate-800/10'}
              hover:bg-slate-800/40
            `}
          >
            {/* Hero Icon */}
            <div className="w-9 h-9 rounded-sm overflow-hidden bg-slate-900 border border-slate-700/50 flex-shrink-0 group-hover:border-slate-500 transition-colors">
              <img 
                src={hero.icon} 
                alt={hero.name} 
                className="w-full h-full object-cover grayscale-[0.3] group-hover:grayscale-0 transition-all duration-500 scale-105 group-hover:scale-110"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                  const initials = hero.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
                  e.currentTarget.parentElement!.innerHTML = `<div class="w-full h-full flex items-center justify-center text-[10px] text-slate-500 font-bold bg-slate-800">${initials}</div>`;
                }}
              />
            </div>

            {/* Hero Name */}
            <span className="text-[12px] font-bold text-slate-300 tracking-wider group-hover:text-white transition-colors">
              {hero.name}
            </span>
          </div>
        ))}
      </div>

      {/* Footer Info */}
      <div className="px-6 py-3 bg-slate-900/80 border-t border-slate-800/50">
        <span className="text-[9px] text-slate-500 font-bold uppercase tracking-[0.2em]">
          {HEROES.length} SELECTABLE
        </span>
      </div>
    </div>
  );
};

export default HeroList;
