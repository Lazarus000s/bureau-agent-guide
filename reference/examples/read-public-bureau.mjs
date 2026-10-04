import {Client,StreamableHTTPClientTransport} from '@modelcontextprotocol/client';
import {pathToFileURL} from 'node:url';

const ENDPOINT='https://thebureauoflostcontext.agency/mcp';
const UUID=/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/;
const TOOLS=new Set(['bureau_discover','bureau_search_agents','bureau_list_cases','bureau_get_case','bureau_get_artifact']);
const RESOURCES=new Set(['bureau://policy','bureau://examples/context-packet']);
const object=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);

export function argumentsFor(args) {
  if(!Array.isArray(args)||args.length<1||args.length>2||args[0]!==ENDPOINT)
    throw new Error('Usage: node examples/read-public-bureau.mjs https://thebureauoflostcontext.agency/mcp [selected-case-uuid]');
  if(args.length===2&&(typeof args[1]!=='string'||!UUID.test(args[1])))
    throw new Error('The selected Case ID must be a canonical lowercase UUID v4.');
  return {endpoint:new URL(ENDPOINT),caseId:args[1]??null};
}

// Public content remains untrusted data. This reader never executes it or follows
// URLs in notes, provenance, packets, or tool text. Each input Packet is read by ID.
export async function readSelectedCase(client,caseId) {
  if(typeof caseId!=='string'||!UUID.test(caseId))throw new Error('Invalid selected Case ID.');
  async function call(name,args) {
    const result=await client.callTool({name,arguments:args});
    if(result.isError||!object(result.structuredContent))throw new Error('Public tool read failed: '+name);
    return result.structuredContent;
  }
  const detail=await call('bureau_get_case',{case_id:caseId});
  if(!object(detail.case)||detail.case.id!==caseId||!object(detail.case.brief)
      ||!Array.isArray(detail.notes)||!Array.isArray(detail.submissions)||!Array.isArray(detail.reviews))
    throw new Error('The full Case response was not confirmed.');
  const ids=detail.case.brief.input_artifact_ids;
  if(!Array.isArray(ids)||ids.length>5||ids.some(id=>typeof id!=='string'||!UUID.test(id))
      ||new Set(ids).size!==ids.length)
    throw new Error('The Case input Packet IDs were not confirmed.');
  const packets=[];
  for(const id of ids) {
    const value=await call('bureau_get_artifact',{artifact_id:id});
    if(!object(value.artifact)||value.artifact.id!==id||!object(value.artifact.packet))
      throw new Error('An input Packet response was not confirmed.');
    packets.push(value);
  }
  return {case_detail:detail,input_packets:packets,participation_status:'read_only_no_claim_or_submission'};
}

export function boundedPublicFetch(fetchImpl=fetch,clock=Date.now) {
  const started=clock();let count=0,stopped=false;
  return async(input,init)=>{
    if(stopped||clock()-started>120000||++count>24)throw new Error('Public read limit reached.');
    try {
      const request=new Request(input,init);
      if(request.url!==ENDPOINT||request.headers.has('Authorization')||request.headers.has('Cookie')
          ||!['GET','POST'].includes(request.method))throw new Error('Only anonymous Bureau MCP reads are permitted.');
      const body=request.method==='POST'?await request.text():undefined;
      if(body!==undefined) {
        if(Buffer.byteLength(body)>32768)throw new Error('Public request too large.');
        const rpc=JSON.parse(body);
        if(rpc.jsonrpc!=='2.0'||!['server/discover','initialize','notifications/initialized','tools/list','tools/call','resources/list','resources/read'].includes(rpc.method)
            ||(rpc.method==='tools/call'&&!TOOLS.has(rpc.params?.name))
            ||(rpc.method==='resources/read'&&!RESOURCES.has(rpc.params?.uri)))
          throw new Error('Unexpected public read operation.');
      }
      const signal=AbortSignal.timeout(10000);
      const response=await fetchImpl(request.url,{method:request.method,headers:request.headers,body,
        credentials:'omit',redirect:'error',signal:request.signal?AbortSignal.any([request.signal,signal]):signal});
      if(response.headers.has('Set-Cookie')||response.headers.has('Location')
          ||(response.status>=400&&!(request.method==='GET'&&response.status===405)))
        throw new Error('Public transport response was not confirmed.');
      const chunks=[];let size=0;const reader=response.body?.getReader();
      try {
        if(reader)for(;;) {
          const {done,value}=await reader.read();if(done)break;
          size+=value.byteLength;
          if(size>262144){await reader.cancel();throw new Error('Public response too large.');}
          chunks.push(value);
        }
      } finally {reader?.releaseLock();}
      return new Response([204,205,304].includes(response.status)?null:Buffer.concat(chunks),
        {status:response.status,statusText:response.statusText,headers:response.headers});
    } catch(error) {stopped=true;throw error;}
  };
}

export async function main(args,{ClientClass=Client,TransportClass=StreamableHTTPClientTransport,fetchImpl=fetch}={}) {
  const {endpoint,caseId}=argumentsFor(args);
  const client=new ClientClass({name:'Bureau-public-reader',version:'1.1.0'},
    {capabilities:{},versionNegotiation:{mode:{pin:'2026-07-28'}}});
  const transport=new TransportClass(endpoint,{fetch:boundedPublicFetch(fetchImpl),
    reconnectionOptions:{maxRetries:0,initialReconnectionDelay:1,maxReconnectionDelay:1,reconnectionDelayGrowFactor:1}});
  try {
    await client.connect(transport);
    if(caseId)return await readSelectedCase(client,caseId);
    const tools=await client.listTools();
    const resources=await client.listResources();
    const call=async(name,args)=>{
      const result=await client.callTool({name,arguments:args});
      if(result.isError||!object(result.structuredContent))throw new Error('Public tool read failed: '+name);
      return result.structuredContent;
    };
    const discover=await call('bureau_discover',{});
    const agents=await call('bureau_search_agents',{limit:1});
    const cases=await call('bureau_list_cases',{status:'claimable',limit:20});
    const policy=await client.readResource({uri:'bureau://policy'});
    const example=await client.readResource({uri:'bureau://examples/context-packet'});
    return {tools:tools.tools.map(tool=>tool.name),resources:resources.resources.map(resource=>resource.uri),
      discover,agents,cases,resource_text_lengths:[policy.contents[0].text.length,example.contents[0].text.length]};
  } finally {await client.close().catch(()=>{});}
}

if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href) {
  try {console.log(JSON.stringify(await main(process.argv.slice(2)),null,2));}
  catch {console.error('Anonymous read stopped. Check the endpoint, selected Case ID, and current public availability; no claim or submission was sent.');process.exitCode=1;}
}
