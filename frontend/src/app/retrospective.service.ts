import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/do';
import 'rxjs/add/operator/map';
import { of } from 'rxjs/observable/of';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable()
export class RetrospectiveService {

  private host = 'http://retrospective-dev.us-east-1.elasticbeanstalk.com';
  private url = this.host + '/api/retro';

  private uuid = '';
  private token = '';

  constructor(private http: HttpClient) { }

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
}
