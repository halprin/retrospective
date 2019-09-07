import {Injectable, NgZone} from '@angular/core';
import { RetrospectiveService } from './retrospective.service';
import { HttpClient } from '@angular/common/http';
import {Observable} from 'rxjs';
import {map} from 'rxjs/operators';

@Injectable()
export class RetrospectiveServiceV2 extends RetrospectiveService {

  constructor(protected http: HttpClient, protected zone: NgZone) {
    super(http, zone, '2');
  }

  groupIssue(issue_id: string, group_id: string): Observable<any> {
    return this.http.put<any>(this.httpUrl + '/' + this.uuid + '/issue/' + issue_id, {
      group: group_id
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    });
  }

  ungroupIssue(issue_id: string): Observable<any> {
    return this.http.put<any>(this.httpUrl + '/' + this.uuid + '/issue/' + issue_id, {
      group: false
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    });
  }

  addGroup(title: string, section: string): Observable<any> {
    return this.http.post<any>(this.httpUrl + '/' + this.uuid + '/group', {
      title: title,
      section: section
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    })
    .pipe(map(json => json.id));
  }

  voteForGroup(group_id: string): Observable<any> {
    return this.http.put<any>(this.httpUrl + '/' + this.uuid + '/group/' + group_id, {
      vote: true
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    });
  }

  unvoteForGroup(group_id: string): Observable<any> {
    return this.http.put<any>(this.httpUrl + '/' + this.uuid + '/group/' + group_id, {
      vote: false
    }, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    });
  }

  deleteGroup(group_id: string): Observable<any> {
    return this.http.delete<any>(this.httpUrl + '/' + this.uuid + '/group/' + group_id, {
      headers: {
        Authorization: 'Bearer ' + this.token,
        'Api-Version': this.version
      }
    });
  }
}
