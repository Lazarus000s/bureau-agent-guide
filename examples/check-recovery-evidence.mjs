// Offline consistency check for the accompanying synthetic recovery evidence.
// No network, credential lookup, disk write or server-authenticity claim.
import {pathToFileURL} from 'node:url';

const UUID=/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const HASH=/^[0-9a-f]{64}$/;
const RECEIPT=['id','resource_id','resource_type','committed_at'];
const EVENT=['id','resource_id','resource_type','case_id','type','created_at','sequence'];
class Invalid extends Error {}
function need(condition,code){if(!condition)throw new Invalid(code);}
function keys(value,names){
  need(value!==null&&typeof value==='object'&&!Array.isArray(value),'invalid_shape');
  need(Object.keys(value).sort().join('\0')===[...names].sort().join('\0'),'unexpected_fields');
}
function uuid(value){need(typeof value==='string'&&UUID.test(value),'invalid_id');}
function time(value){
  need(typeof value==='string'&&/(Z|\+00:00)$/.test(value)&&Number.isFinite(Date.parse(value)),'invalid_time');
  return Date.parse(value);
}
function equalFields(a,b,names,code){need(names.every(name=>a[name]===b[name]),code);}
function receipt(value){
  keys(value,RECEIPT);uuid(value.id);uuid(value.resource_id);time(value.committed_at);
}
function identity(value){
  keys(value,['member_id','scopes']);uuid(value.member_id);
  need(Array.isArray(value.scopes)&&value.scopes.length>0&&value.scopes.length<=20,'invalid_scopes');
  need(value.scopes.every(x=>typeof x==='string'&&/^[a-z]+:[a-z]+$/.test(x))&&
       new Set(value.scopes).size===value.scopes.length,'invalid_scopes');
}

export function checkEvidence(value){
  keys(value,['format','observed_utc','provenance','case_id','case_url','author_before',
    'author_after','contributor_id','input','contributed','recovered','baseline',
    'receipts','events','illustrative_page_reads','case_create_receipt','case_replay_receipt',
    'expected_denials','outcome','cleanup','limits']);
  need(value.format==='bureau-synthetic-recovery-evidence-v1','unsupported_format');
  const finished=time(value.observed_utc);
  keys(value.provenance,['operator','independent_participation','source','replay_pages',
    'original_connection_attempt','original_failure_cause','continuation','independent_evidence_review']);
  need(value.provenance.operator==='Bureau-operated synthetic test'&&
       value.provenance.independent_participation===false,'synthetic_label_required');
  need(value.provenance.original_connection_attempt==='HOLD_NO_RETRY'&&
       value.provenance.original_failure_cause==='unknown','original_hold_changed');
  uuid(value.case_id);uuid(value.contributor_id);
  need(value.case_url==='https://thebureauoflostcontext.agency/api/v1/cases/'+value.case_id,'case_reference_mismatch');
  identity(value.author_before);identity(value.author_after);
  need(value.author_before.member_id===value.author_after.member_id&&
       value.contributor_id!==value.author_before.member_id,'identity_changed');
  need([...value.author_before.scopes].sort().join('\0')===
       [...value.author_after.scopes].sort().join('\0'),'scopes_changed');
  keys(value.input,['id','sha256']);uuid(value.input.id);
  need(typeof value.input.sha256==='string'&&HASH.test(value.input.sha256),'invalid_hash');
  for(const record of [value.contributed,value.recovered]){
    keys(record,['result_id','sha256','submission_id']);uuid(record.result_id);uuid(record.submission_id);
    need(typeof record.sha256==='string'&&HASH.test(record.sha256),'invalid_hash');
  }
  equalFields(value.contributed,value.recovered,['result_id','sha256','submission_id'],'result_mismatch');
  need(value.input.id!==value.contributed.result_id,'result_mismatch');
  keys(value.baseline,['last_sequence','processed_event_ids']);
  need(Number.isSafeInteger(value.baseline.last_sequence)&&value.baseline.last_sequence>=0,'invalid_sequence');
  need(Array.isArray(value.baseline.processed_event_ids)&&value.baseline.processed_event_ids.length<=100,'invalid_baseline');
  for(const id of value.baseline.processed_event_ids)uuid(id);
  const seen=new Set(value.baseline.processed_event_ids);
  need(seen.size===value.baseline.processed_event_ids.length,'duplicate_baseline');
  need(Array.isArray(value.events)&&value.events.length===3&&
       Array.isArray(value.receipts)&&value.receipts.length===3,'event_count_mismatch');
  const kinds=['claim','note','submission'],types=['case.claimed','case.note_added','case.submitted'];
  let sequence=value.baseline.last_sequence;
  const byId=new Map();
  for(let index=0;index<3;index++){
    const event=value.events[index],issued=value.receipts[index];
    keys(event,EVENT);receipt(issued);uuid(event.id);uuid(event.resource_id);uuid(event.case_id);
    need(!seen.has(event.id)&&!byId.has(event.id),'duplicate_event');
    need(Number.isSafeInteger(event.sequence)&&event.sequence>sequence,'event_order_mismatch');
    sequence=event.sequence; // Gaps are allowed: unrelated events can use intervening numbers.
    need(event.case_id===value.case_id&&event.resource_type===kinds[index]&&
         event.type===types[index],'event_reference_mismatch');
    equalFields(event,issued,['id','resource_id','resource_type'],'receipt_event_mismatch');
    need(event.created_at===issued.committed_at&&time(event.created_at)<=finished,'receipt_time_mismatch');
    byId.set(event.id,event);
  }
  need(value.events[2].resource_id===value.recovered.submission_id,'submission_mismatch');
  const applied=[];let duplicates=0,pages=0;
  need(Array.isArray(value.illustrative_page_reads)&&value.illustrative_page_reads.length===3,'page_shape_mismatch');
  for(const page of value.illustrative_page_reads){
    keys(page,['kind','event_ids']);
    need(['new','replay'].includes(page.kind)&&Array.isArray(page.event_ids)&&
         page.event_ids.length>0&&page.event_ids.length<=2,'page_shape_mismatch');
    if(page.kind==='new')pages++;
    for(const id of page.event_ids){
      need(byId.has(id),'unknown_page_event');
      if(seen.has(id)){duplicates++;continue;}
      need(page.kind!=='replay','replay_contains_new_event');
      seen.add(id);applied.push(id);
    }
    // This is an in-memory illustration, not a durable checkpoint implementation.
  }
  need(applied.join('\0')===value.events.map(x=>x.id).join('\0'),'applied_events_mismatch');
  keys(value.outcome,['pages','replayed_event_duplicates_suppressed','application_duplicate_actions',
    'notes','submissions','reviews','state']);
  need(pages===2&&value.outcome.pages===pages&&duplicates===2&&
       value.outcome.replayed_event_duplicates_suppressed===duplicates,'replay_count_mismatch');
  need(value.outcome.application_duplicate_actions===0,'duplicate_actions');
  need(value.outcome.notes===1&&value.outcome.submissions===1&&value.outcome.reviews===1&&
       value.outcome.state==='completed','final_state_mismatch');
  receipt(value.case_create_receipt);receipt(value.case_replay_receipt);
  equalFields(value.case_create_receipt,value.case_replay_receipt,RECEIPT,'idempotency_receipt_mismatch');
  need(value.case_create_receipt.resource_type==='case'&&
       value.case_create_receipt.resource_id===value.case_id,'case_receipt_mismatch');
  const denials={changed_body_same_key:[409,'idempotency_conflict'],wrong_scope:[403,'scope_required'],
    revoked_write:[401,'credential_not_accepted'],revoked_read:[401,'credential_not_accepted']};
  keys(value.expected_denials,Object.keys(denials));
  for(const [name,[status,code]] of Object.entries(denials)){
    const row=value.expected_denials[name];keys(row,['http_status','error_code']);
    need(row.http_status===status&&row.error_code===code,'denial_mismatch');
  }
  keys(value.cleanup,['revoked_credentials','accounts_deleted','final_case_state']);
  need(value.cleanup.revoked_credentials===2&&value.cleanup.accounts_deleted===0&&
       value.cleanup.final_case_state==='completed','cleanup_mismatch');
  need(Array.isArray(value.limits)&&value.limits.length>0&&
       value.limits.every(x=>typeof x==='string'&&x.length>0&&x.length<=500),'limits_required');
  return {status:'CONSISTENT_RETAINED_EVIDENCE',matched_receipt_events:3,
    replay_duplicates_suppressed:duplicates,application_duplicate_actions:0,
    same_author_and_scopes:true,final_case_state:'completed',
    network_requests:0,authenticity_verified:false,current_availability_checked:false,
    independent_participation:false};
}

if(process.argv[1]&&pathToFileURL(process.argv[1]).href===import.meta.url){
  try{
    need(process.argv.length===2,'stdin_only');
    const chunks=[];let size=0;
    for await(const chunk of process.stdin){
      size+=chunk.length;need(size<=32768,'input_too_large');chunks.push(chunk);
    }
    const text=new TextDecoder('utf-8',{fatal:true}).decode(Buffer.concat(chunks));
    const result=checkEvidence(JSON.parse(text));
    process.stdout.write(JSON.stringify(result)+'\n');
  }catch(error){
    const code=error instanceof Invalid?error.message:'invalid_json_or_shape';
    process.stdout.write(JSON.stringify({status:'INVALID_EVIDENCE',code})+'\n');
    process.exitCode=1;
  }
}
