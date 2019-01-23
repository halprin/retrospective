import { NgZone } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/do';
import 'rxjs/add/operator/map';
import { HttpClient } from '@angular/common/http';
import { environment } from '../environments/environment';
import { Observer } from "rxjs/Observer";

export class RetrospectiveService {

  private host = environment.backendEndpoint;
  private wsHost = environment.backendWsEndpoint;
  protected httpUrl = 'https://' + this.host + '/api/retro';
  private wsUrl = 'wss://' + this.wsHost + '/retro';

  private liveUpdateSocket: WebSocket;

  protected uuid = '';
  protected token = '';

  constructor(protected http: HttpClient, protected zone: NgZone, protected version: string = '1') { }

  startRetrospective(retroName: string, userName: string): Observable<any> {
    return this.http.post<any>(this.httpUrl, {
      retroName: retroName,
      adminName: userName
    }, {
      headers: {
        'Api-Version': this.version
      }
    })
    .do(json => {
      this.uuid = json.retroId;
      this.token = json.token;
    })
    .map(json => json.retroId);
  }

  joinRetrospective(retroId: string, userName: string): Observable<any> {
    this.uuid = retroId;
    return this.http.post<any>(this.httpUrl + '/' + this.uuid + '/user', {
      name: userName
    }, {
      headers: {
        'Api-Version': this.version
      }
    })
    .do(json => {
      this.token = json.token;
    })
    .map(json => this.uuid);
  }

  getRetrospective(): Observable<any> {
    return this.http.get<any>(this.httpUrl + '/' + this.uuid, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    });
  }

  startLiveUpdateRetrospective(): Observable<MessageEvent> {
    if(!this.liveUpdateSocket || this.liveUpdateSocket.readyState !== WebSocket.OPEN) {
      this.liveUpdateSocket = new WebSocket(this.wsUrl + '?uuid=' + this.uuid + '&token=' + this.token + '&version=' + this.version);
    }

    let liveUpdaterObservable = Observable.create(
      (observer: Observer<MessageEvent>) => {
        this.liveUpdateSocket.onmessage = message => {
          this.zone.run(() => observer.next(message))
        };
        this.liveUpdateSocket.onerror = observer.error.bind(observer);
        this.liveUpdateSocket.onclose = observer.complete.bind(observer);
        return this.liveUpdateSocket.close.bind(this.liveUpdateSocket);
      }
    );

    return liveUpdaterObservable;
  }

  markUserAsReady(): Observable<any> {
    return this.http.put<any>(this.httpUrl + '/' + this.uuid + '/user', {
      ready: true
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    });
  }

  markUserAsNotReady(): Observable<any> {
    return this.http.put<any>(this.httpUrl + '/' + this.uuid + '/user', {
      ready: false
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    });
  }

  addIssue(title: string, section: string): Observable<any> {
    return this.http.post<any>(this.httpUrl + '/' + this.uuid + '/issue', {
      title: title,
      section: section
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    })
    .map(json => json.id);
  }

  deleteIssue(issue_id: string): Observable<any> {
    return this.http.delete<any>(this.httpUrl + '/' + this.uuid + '/issue/' + issue_id, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    });
  }

  moveRetrospectiveBackward(): Observable<any> {
    return this.http.put<any>(this.httpUrl + '/' + this.uuid, {
      direction: 'previous'
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    })
    .map(json => json.newStep);
  }

  moveRetrospectiveForward(): Observable<any> {
    return this.http.put<any>(this.httpUrl + '/' + this.uuid, {
      direction: 'next'
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    })
    .map(json => json.newStep);
  }

  voteForIssue(issue_id: string): Observable<any> {
    return this.http.put<any>(this.httpUrl + '/' + this.uuid + '/issue/' + issue_id, {
      vote: true
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    });
  }

  unvoteForIssue(issue_id: string): Observable<any> {
    return this.http.put<any>(this.httpUrl + '/' + this.uuid + '/issue/' + issue_id, {
      vote: false
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    });
  }
}
