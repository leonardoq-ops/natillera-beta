/**
 * Natillera Digital — Savings Wheel
 * Generates the 12-month SVG wheel dynamically.
 * Drop the frog image in assets/frog.png — it will auto-appear.
 */
(function () {
    'use strict';

    const NS  = 'http://www.w3.org/2000/svg';
    const CX  = 250, CY = 250;   // SVG centre (viewBox 500×500)

    // Ring [outerRadius, innerRadius]
    const MONTH_RING = [238, 170];
    const MOON_RING  = [165, 128];
    const GOLD_RING  = [123, 108];
    const CENTER_R   = 104;

    const MONTHS = [
        'Enero','Febrero','Marzo','Abril','Mayo','Junio',
        'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'
    ];

    const C = {
        green_future : '#0A3A1E',
        green_done   : '#14562F',
        gold         : '#D4AF37',
        gold_dark    : '#8B6914',
        gold_light   : '#F4D03F',
        navy         : '#07102A',
        lapis        : '#1A2F72',   // deep lapis-lazuli blue for moon ring
        lapis_dark   : '#0D1A4A',
        brown        : '#4A2800',
    };

    /* ── helpers ───────────────────────────────────────────────── */

    function el(tag, attrs) {
        const e = document.createElementNS(NS, tag);
        if (attrs) Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
        return e;
    }

    function txt(content, attrs) {
        const e = el('text', attrs);
        e.textContent = content;
        return e;
    }

    // Polar → Cartesian  (0° = top, clockwise)
    function polar(r, deg) {
        const a = (deg - 90) * Math.PI / 180;
        return [CX + r * Math.cos(a), CY + r * Math.sin(a)];
    }

    // Donut arc path between two radii and two angles
    function arc(ro, ri, a1, a2) {
        const lg = (a2 - a1) > 180 ? 1 : 0;
        const [x1,y1] = polar(ro, a1);
        const [x2,y2] = polar(ro, a2);
        const [x3,y3] = polar(ri, a2);
        const [x4,y4] = polar(ri, a1);
        return `M${x1},${y1}A${ro},${ro},0,${lg},1,${x2},${y2}` +
               `L${x3},${y3}A${ri},${ri},0,${lg},0,${x4},${y4}Z`;
    }

    /* ── month status ───────────────────────────────────────────── */

    const today      = new Date();
    const thisMonth  = today.getMonth();   // 0 = January

    function status(i) {
        if (i <  thisMonth) return 'done';
        if (i === thisMonth) return 'current';
        return 'future';
    }

    /* ── main build ─────────────────────────────────────────────── */

    function build(svg) {
        const defs = el('defs');
        svg.appendChild(defs);

        /* gradients */
        function radGrad(id, stops) {
            const g = el('radialGradient', {id, cx:'50%', cy:'50%', r:'50%'});
            stops.forEach(([off, color]) => {
                const s = el('stop', {offset: off});
                s.style.stopColor = color;
                g.appendChild(s);
            });
            defs.appendChild(g);
        }
        radGrad('gGold',   [['0%','#F4D03F'],['55%','#D4AF37'],['100%','#6E4E08']]);
        radGrad('gCenter', [['0%','#FFFDF8'],['60%','#F5EDDB'],['100%','#E8D9B8']]);

        /* glow filter for current month */
        const filt = el('filter', {id:'glow', x:'-40%', y:'-40%', width:'180%', height:'180%'});
        const fblur = el('feGaussianBlur', {in:'SourceGraphic', stdDeviation:'5', result:'b'});
        const fmerge = el('feMerge');
        ['b','SourceGraphic'].forEach(n => fmerge.appendChild(el('feMergeNode', {in:n})));
        filt.appendChild(fblur);
        filt.appendChild(fmerge);
        defs.appendChild(filt);

        /* curved text paths — one per month */
        const TR = (MONTH_RING[0] + MONTH_RING[1]) / 2 + 1;
        MONTHS.forEach((_, i) => {
            const a1  = i * 30, a2 = a1 + 30, mid = a1 + 15;
            const lower = mid > 90 && mid < 270;
            let d;
            if (lower) {
                const [ex,ey] = polar(TR, a2);
                const [sx,sy] = polar(TR, a1);
                d = `M${ex},${ey}A${TR},${TR},0,0,0,${sx},${sy}`;
            } else {
                const [sx,sy] = polar(TR, a1);
                const [ex,ey] = polar(TR, a2);
                d = `M${sx},${sy}A${TR},${TR},0,0,1,${ex},${ey}`;
            }
            defs.appendChild(el('path', {id:`mp${i}`, d, fill:'none'}));
        });

        /* ── outer bevel border (3-ring 3-D effect) ── */
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:247,fill:'none',stroke:C.gold_dark,'stroke-width':'5'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:244,fill:'none',stroke:C.gold,'stroke-width':'3.5'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:242,fill:'none',stroke:C.gold_light,'stroke-width':'1.2'}));

        /* ── month segments ── */
        MONTHS.forEach((name, i) => {
            const GAP = 0.7;
            const a1  = i * 30 + GAP / 2;
            const a2  = (i + 1) * 30 - GAP / 2;
            const mid = i * 30 + 15;
            const s   = status(i);

            const fill = s === 'current' ? C.gold :
                         s === 'done'    ? C.green_done :
                                           C.green_future;

            const seg = el('path', {
                d: arc(MONTH_RING[0], MONTH_RING[1], a1, a2),
                fill, stroke: C.gold, 'stroke-width':'0.8',
                class: `ws-${s}`
            });
            if (s === 'current') seg.setAttribute('filter', 'url(#glow)');
            svg.appendChild(seg);

            /* gold divider line */
            const [lx1,ly1] = polar(MONTH_RING[0], i * 30);
            const [lx2,ly2] = polar(MONTH_RING[1], i * 30);
            svg.appendChild(el('line', {x1:lx1,y1:ly1,x2:lx2,y2:ly2,stroke:C.gold,'stroke-width':'2'}));

            /* curved month name */
            const fontSize = name.length > 8 ? '8' : name.length > 6 ? '9.5' : '10.5';
            const t  = el('text', {
                fill: s === 'current' ? C.brown : C.gold,
                'font-size': fontSize,
                'font-family': 'Montserrat, sans-serif',
                'font-weight': '700',
                'letter-spacing': '0.5'
            });
            const tp = el('textPath', {href:`#mp${i}`, startOffset:'50%', 'text-anchor':'middle'});
            tp.textContent = name;
            t.appendChild(tp);
            svg.appendChild(t);

            /* small completion dot on done months */
            if (s === 'done') {
                const [dx,dy] = polar(MONTH_RING[1] + 7, mid);
                svg.appendChild(el('circle', {cx:dx,cy:dy,r:3,fill:C.gold,opacity:'0.65'}));
            }
        });

        /* year-progress arc along inner edge of month ring */
        const pct = (thisMonth + today.getDate() / 31) / 12;
        const pAngle = pct * 360;
        if (pAngle > 0.5) {
            const pr = MONTH_RING[1] + 5;
            const [px1,py1] = polar(pr, 0);
            const [px2,py2] = polar(pr, Math.min(pAngle, 359.9));
            svg.appendChild(el('path', {
                d: `M${px1},${py1}A${pr},${pr},0,${pAngle>180?1:0},1,${px2},${py2}`,
                fill:'none', stroke:C.gold_light,
                'stroke-width':'3', 'stroke-linecap':'round', opacity:'0.55'
            }));
        }

        /* ── moon phase ring — lapis lazuli ── */
        const moonMid = (MOON_RING[0] + MOON_RING[1]) / 2;
        const moonW   = MOON_RING[0] - MOON_RING[1];

        // Lapis background
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:moonMid,fill:'none',stroke:C.lapis,'stroke-width':moonW}));

        // Outer bevel
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:MOON_RING[0]+1.5,fill:'none',stroke:C.gold_dark,'stroke-width':'3'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:MOON_RING[0],    fill:'none',stroke:C.gold,     'stroke-width':'2'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:MOON_RING[0]-1,  fill:'none',stroke:C.gold_light,'stroke-width':'0.8'}));

        // Inner bevel
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:MOON_RING[1]+1,  fill:'none',stroke:C.gold_light,'stroke-width':'0.8'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:MOON_RING[1],    fill:'none',stroke:C.gold,     'stroke-width':'2'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:MOON_RING[1]-1.5,fill:'none',stroke:C.gold_dark,'stroke-width':'3'}));

        // 8 phase icons at 22.5° intervals
        const mr = moonW * 0.30;
        const phases  = [0, 0.25, 0.5, 0.75, 1, 0.75, 0.5, 0.25];
        const waning  = [0,    0,   0,    0, 0,    1,   1,    1];

        phases.forEach((lit, i) => {
            const [mx,my] = polar(moonMid, i * 45 + 22.5);

            svg.appendChild(el('circle', {cx:mx,cy:my,r:mr,fill:C.lapis_dark}));

            if (lit === 1) {
                svg.appendChild(el('circle', {cx:mx,cy:my,r:mr,fill:'#EDE278',opacity:'0.92'}));
            } else if (lit > 0) {
                const cid = `mc${i}`;
                const cp  = el('clipPath', {id:cid});
                const rx = waning[i] ? mx - mr - 1 : mx;
                cp.appendChild(el('rect', {x:rx, y:my-mr-1, width:mr+2, height:(mr+1)*2}));
                defs.appendChild(cp);

                if (lit === 0.5) {
                    svg.appendChild(el('circle', {cx:mx,cy:my,r:mr,fill:'#EDE278',opacity:'0.88','clip-path':`url(#${cid})`}));
                } else if (lit === 0.75) {
                    svg.appendChild(el('circle', {cx:mx,cy:my,r:mr,fill:'#EDE278',opacity:'0.88'}));
                    const did = `md${i}`;
                    const dp  = el('clipPath', {id:did});
                    const dx2 = waning[i] ? mx : mx - mr - 1;
                    dp.appendChild(el('rect', {x:dx2, y:my-mr-1, width:mr+2, height:(mr+1)*2}));
                    defs.appendChild(dp);
                    const offX = waning[i] ? mx + mr*0.52 : mx - mr*0.52;
                    svg.appendChild(el('circle', {cx:offX,cy:my,r:mr*0.86,fill:C.lapis_dark,'clip-path':`url(#${did})`}));
                } else {
                    // crescent (0.25)
                    svg.appendChild(el('circle', {cx:mx,cy:my,r:mr,fill:'#EDE278',opacity:'0.88','clip-path':`url(#${cid})`}));
                    const offX = waning[i] ? mx - mr*0.44 : mx + mr*0.44;
                    svg.appendChild(el('circle', {cx:offX,cy:my,r:mr*0.80,fill:C.lapis_dark}));
                }
            }
        });

        /* ── gold decorative ring with bevel ── */
        const gMid = (GOLD_RING[0] + GOLD_RING[1]) / 2;
        const gW   = GOLD_RING[0] - GOLD_RING[1];
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:gMid,fill:'none',stroke:'url(#gGold)','stroke-width':gW}));

        // Outer bevel
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:GOLD_RING[0]+1.5,fill:'none',stroke:C.gold_dark, 'stroke-width':'3'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:GOLD_RING[0],    fill:'none',stroke:C.gold,      'stroke-width':'2'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:GOLD_RING[0]-1,  fill:'none',stroke:C.gold_light,'stroke-width':'0.8'}));

        // Inner bevel
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:GOLD_RING[1]+1,  fill:'none',stroke:C.gold_light,'stroke-width':'0.8'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:GOLD_RING[1],    fill:'none',stroke:C.gold,      'stroke-width':'2'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:GOLD_RING[1]-1.5,fill:'none',stroke:C.gold_dark, 'stroke-width':'3'}));

        for (let i = 0; i < 24; i++) {
            const [dx,dy] = polar(gMid, i * 15);
            svg.appendChild(el('circle', {cx:dx,cy:dy,r:1.5,fill:C.gold_dark}));
        }

        /* ── center circle with bevel ── */
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:CENTER_R+2,  fill:'none',         stroke:C.gold_dark, 'stroke-width':'4'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:CENTER_R,    fill:'url(#gCenter)',stroke:C.gold,      'stroke-width':'2.5'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:CENTER_R-1.5,fill:'none',         stroke:C.gold_light,'stroke-width':'1'}));
        svg.appendChild(el('circle', {cx:CX,cy:CY,r:CENTER_R-7,  fill:'none',         stroke:C.gold,      'stroke-width':'0.5',opacity:'0.35'}));

        /* sun icon */
        const SY = CY - 35, SR = 9;
        for (let i = 0; i < 16; i++) {
            const a   = i * 22.5 * Math.PI / 180;
            const ri  = i % 2 === 0 ? SR + 3 : SR + 5;
            const ro  = i % 2 === 0 ? SR + 9 : SR + 6;
            const x1  = CX + ri * Math.cos(a), y1 = SY + ri * Math.sin(a);
            const x2  = CX + ro * Math.cos(a), y2 = SY + ro * Math.sin(a);
            svg.appendChild(el('line', {x1,y1,x2,y2,stroke:C.gold,'stroke-width':i%2===0?'1.8':'1.2','stroke-linecap':'round'}));
        }
        svg.appendChild(el('circle', {cx:CX,cy:SY,r:SR,fill:C.gold_light,stroke:C.gold,'stroke-width':'1.5'}));
        svg.appendChild(el('circle', {cx:CX,cy:SY,r:SR*0.45,fill:C.gold_dark,opacity:'0.35'}));

        /* brand text */
        svg.appendChild(txt('Natillera', {
            x:CX, y:CY+8, 'text-anchor':'middle',
            fill:C.brown, 'font-size':'22',
            'font-family':'Crimson Pro, Georgia, serif',
            'font-weight':'700'
        }));
        svg.appendChild(txt('digital', {
            x:CX, y:CY+26, 'text-anchor':'middle',
            fill:C.gold_dark, 'font-size':'13',
            'font-family':'Montserrat, sans-serif',
            'font-weight':'400', 'letter-spacing':'2'
        }));
    }

    /* ── init ── */
    function init() {
        const s = document.getElementById('natilleraWheel');
        if (s) build(s);
    }

    document.readyState === 'loading'
        ? document.addEventListener('DOMContentLoaded', init)
        : init();
})();
