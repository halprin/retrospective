import { Injectable, NgZone } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/do';
import 'rxjs/add/operator/map';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../environments/environment';
import { Observer } from "rxjs/Observer";

@Injectable()
export class RetrospectiveService {

  private host = environment.backendEndpoint;
  private url = this.host + '/api/retro';

  private liveUpdateSocket: WebSocket;

  private uuid = '';
  private token = '';

  constructor(private http: HttpClient, private zone: NgZone) { }

  startRetrospective(retroName: string, userName: string): Observable<any> {
    return this.http.post<any>(this.url, {
      retroName: retroName,
      adminName: userName
    })
    .do(json => {
      this.uuid = json.retroId;
      this.token = json.token;
    })
    .map(json => json.retroId);
  }

  joinRetrospective(retroId: string, userName: string): Observable<any> {
    this.uuid = retroId;
    return this.http.post<any>(this.url + '/' + this.uuid + '/user', {
      name: userName
    })
    .do(json => {
      this.token = json.token;
    })
    .map(json => this.uuid);
  }

  getRetrospective(): Observable<any> {
    return this.http.get<any>(this.url + '/' + this.uuid, {
      headers: {
        Authorization: 'Bearer ' + this.token
      }
    });
  }

  startLiveUpdateRetrospective(): Observable<MessageEvent> {
    if(!this.liveUpdateSocket || this.liveUpdateSocket.readyState !== WebSocket.OPEN) {
      this.liveUpdateSocket = new WebSocket('ws://localhost:8000/api/ws/' + this.uuid, this.token);
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
    return this.http.put<any>(this.url + '/' + this.uuid + '/user', {
      ready: true
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token
      }
    });
  }

  markUserAsNotReady(): Observable<any> {
    return this.http.put<any>(this.url + '/' + this.uuid + '/user', {
      ready: false
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token
      }
    });
  }

  addIssue(title: string, section: string): Observable<any> {
    return this.http.post<any>(this.url + '/' + this.uuid + '/issue', {
      title: title,
      section: section
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token
      }
    })
    .map(json => json.id);
  }

  deleteIssue(issue_id: string): Observable<any> {
    return this.http.delete<any>(this.url + '/' + this.uuid + '/issue/' + issue_id, {
      headers: {
        Authorization: 'Bearer ' + this.token
      }
    });
  }

  moveRetrospectiveBackward(): Observable<any> {
    return this.http.put<any>(this.url + '/' + this.uuid, {
      direction: 'previous'
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token
      }
    })
    .map(json => json.newStep);
  }

  moveRetrospectiveForward(): Observable<any> {
    return this.http.put<any>(this.url + '/' + this.uuid, {
      direction: 'next'
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token
      }
    })
    .map(json => json.newStep);
  }

  voteForIssue(issue_id: string): Observable<any> {
    return this.http.put<any>(this.url + '/' + this.uuid + '/issue/' + issue_id, {
      vote: true
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token
      }
    });
  }

  unvoteForIssue(issue_id: string): Observable<any> {
    return this.http.put<any>(this.url + '/' + this.uuid + '/issue/' + issue_id, {
      vote: false
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token
      }
    });
  }
}
