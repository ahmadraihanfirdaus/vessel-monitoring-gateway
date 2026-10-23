#include <stdio.h>
#include <stdint.h>
#include "phase9_b16_receipt_gate.h"
static int ok(int x){return !!x;}
int main(void){
    phase9_b8_ack_window window;
    vg_b16_receipt_t r={201u,VG_B16_TELEMETRY_CREATED,1u,11u,true,true};
    unsigned tests=0;
    phase9_b8_ack_init(&window);
#define EXPECT(condition) do{++tests;if(!ok(condition)){fprintf(stderr,"CASE_%u_FAILED\n",tests);return 1;}}while(0)
    EXPECT(phase9_b8_ack_begin(&window,1u,11u));
    r.authenticated_response_verified=false;
    EXPECT(!vg_b16_commit_receipt(&window,r) && window.pending && window.last_accepted_sequence==0u);
    r.authenticated_response_verified=true;r.local_safety_pass=false;
    EXPECT(!vg_b16_commit_receipt(&window,r) && window.pending);
    r.local_safety_pass=true;r.correlation=12u;
    EXPECT(!vg_b16_commit_receipt(&window,r) && window.pending);
    r.correlation=11u;r.http_status=409u;r.decoded_result=VG_B16_CONFLICT;
    EXPECT(!vg_b16_commit_receipt(&window,r) && window.pending);
    r.http_status=503u;r.decoded_result=VG_B16_DEPENDENCY_UNAVAILABLE;
    EXPECT(!vg_b16_commit_receipt(&window,r) && window.pending);
    r.http_status=401u;r.decoded_result=VG_B16_UNAUTHORIZED;
    EXPECT(!vg_b16_commit_receipt(&window,r) && window.pending);
    r.http_status=201u;r.decoded_result=VG_B16_EVENT_IDENTICAL;
    EXPECT(!vg_b16_commit_receipt(&window,r) && window.pending);
    r.http_status=200u;r.decoded_result=VG_B16_TELEMETRY_CREATED;
    EXPECT(!vg_b16_commit_receipt(&window,r) && window.pending);
    r.http_status=201u;r.decoded_result=VG_B16_TELEMETRY_CREATED;
    EXPECT(vg_b16_commit_receipt(&window,r) && !window.pending && window.last_accepted_sequence==1u);
    EXPECT(!vg_b16_commit_receipt(&window,r));
    EXPECT(phase9_b8_ack_begin(&window,2u,22u));
    r.sequence=2u;r.correlation=22u;r.http_status=200u;r.decoded_result=VG_B16_TELEMETRY_IDENTICAL;
    EXPECT(vg_b16_commit_receipt(&window,r) && window.last_accepted_sequence==2u);
    EXPECT(phase9_b8_ack_begin(&window,3u,33u));
    r.sequence=3u;r.correlation=33u;r.http_status=201u;r.decoded_result=VG_B16_EVENT_PERSISTED;
    EXPECT(vg_b16_commit_receipt(&window,r) && window.last_accepted_sequence==3u);
    EXPECT(phase9_b8_ack_begin(&window,4u,44u));
    r.sequence=4u;r.correlation=44u;r.http_status=200u;r.decoded_result=VG_B16_EVENT_IDENTICAL;
    EXPECT(vg_b16_commit_receipt(&window,r) && window.last_accepted_sequence==4u);
    EXPECT(!phase9_b8_ack_begin(&window,4u,44u));
    EXPECT(phase9_b8_ack_begin(&window,5u,55u));
    r.sequence=5u;r.correlation=55u;r.http_status=500u;r.decoded_result=VG_B16_TELEMETRY_CREATED;
    EXPECT(!vg_b16_commit_receipt(&window,r) && window.last_accepted_sequence==4u);
    phase9_b8_ack_cancel(&window);
    EXPECT(!window.pending && window.last_accepted_sequence==4u);
    printf("B16_RECEIPT_GATE=PASS_%u_CASES_HOST_ONLY\n",tests);
    return 0;
}
