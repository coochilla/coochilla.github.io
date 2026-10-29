/* Public profile counts refresh weekly in GitHub Actions. No browser polling. */
(() => {
  'use strict';
  const get=id=>document.getElementById(id);
  const number=n=>new Intl.NumberFormat('en-GB').format(n);
  const date=s=>new Intl.DateTimeFormat('en-GB',{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(s+'T12:00:00Z')).toLowerCase();
  function validate(data){
    if(data?.schemaVersion!==1||data.artistId!=='2KMHj8v88gQE6fQZNMp9Qc')throw new Error('wrong artist');
    for(const key of ['listeners','followers'])if(!Number.isSafeInteger(data.metrics?.[key])||data.metrics[key]<0)throw new Error('invalid count');
    if(!/^\d{4}-\d{2}-\d{2}$/.test(data.verifiedOn)||Number.isNaN(Date.parse(data.verifiedOn)))throw new Error('invalid verification date');
    return data;
  }
  function showStatus(message){get('metrics-status').textContent=message;get('metrics-status').hidden=!message;}
  let current=null;
  function show(data){
    validate(data);
    if(current&&data.verifiedOn<current.verifiedOn)throw new Error('older capture');
    current=data;
    get('audience-value').textContent=number(data.metrics.listeners);
    get('metric-followers').textContent=number(data.metrics.followers);
    get('audience-note').textContent='source: spotify artist profile';
    get('metrics-updated').textContent='checked '+date(data.verifiedOn)+' · refreshed weekly';
    for(const artwork of document.querySelectorAll('[data-track-id]')){
      const track=data.tracks?.[artwork.dataset.trackId];
      const count=artwork.querySelector('.track-streams'),checked=artwork.querySelector('.track-checked');
      const valid=Number.isSafeInteger(track?.streams)&&track.streams>=0&&/^\d{4}-\d{2}-\d{2}$/.test(track.verifiedOn)&&!Number.isNaN(Date.parse(track.verifiedOn));
      count.hidden=checked.hidden=!valid;
      if(valid){count.textContent=number(track.streams)+' spotify streams';checked.textContent='checked '+date(track.verifiedOn);}
    }
    const stale=(Date.now()-Date.parse(data.verifiedOn+'T00:00:00Z'))>10*86400000;
    showStatus(stale?'latest available figures · a newer update is pending.':'');
  }
  const snapshot=window.COOCHILLA_METRICS;
  if(snapshot?.artistId==='2KMHj8v88gQE6fQZNMp9Qc'){
    get('snapshot-period').textContent=date(snapshot.period.from)+' – '+date(snapshot.period.to);
    const labels={streams:'streams',monthlyActiveListeners:'monthly active listeners',saves:'saves',playlistAdds:'playlist adds'};
    for(const [key,label] of Object.entries(labels)){
      if(!Number.isSafeInteger(snapshot.metrics[key]))continue;
      const row=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');
      row.className='metric-card';dt.textContent=label;dd.textContent=number(snapshot.metrics[key]);row.append(dt,dd);get('metrics-details').append(row);
    }
    const series=snapshot.dailyListeners||[];
    if(series.length>1&&series.every(p=>Number.isSafeInteger(p.value)&&p.value>=0)){
      const max=Math.max(...series.map(p=>p.value),1);
      get('listeners-line').setAttribute('points',series.map((p,i)=>(8+i*584/(series.length-1)).toFixed(1)+','+(102-p.value*94/max).toFixed(1)).join(' '));
      get('listeners-chart').hidden=false;
    }
  }else get('dashboard-snapshot').hidden=true;
  if(window.COOCHILLA_PUBLIC){try{show(window.COOCHILLA_PUBLIC);}catch(e){get('audience-value').textContent='—';}}
  if(location.protocol!=='file:')fetch('spotify-public.json',{cache:'no-cache'})
    .then(r=>{if(!r.ok)throw new Error('feed unavailable');return r.json();}).then(show)
    .catch(()=>showStatus(current?'showing the last checked spotify figures.':'spotify figures are temporarily unavailable.'));
})();
