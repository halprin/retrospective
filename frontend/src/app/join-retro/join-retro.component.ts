import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpErrorResponse} from '@angular/common/http'
import { RetrospectiveServiceV2 } from '../retrospectiveV2.service'

@Component({
  selector: 'app-join-retro',
  templateUrl: './join-retro.component.html',
  styleUrls: ['./join-retro.component.css']
})
export class JoinRetroComponent implements OnInit {

  errorText = '';
  routeRetroId = '';
  joinButtonText = 'Join';

  constructor(private router: Router, private retroService: RetrospectiveServiceV2, private route: ActivatedRoute) { }

  ngOnInit() {
    this.routeRetroId = this.route.snapshot.paramMap.get('id');
  }

  joinRetro(retroId: string, userName: string): void {
    this.startLoadingIndicator();
    this.retroService.joinRetrospective(retroId, userName)
      .subscribe(uuid => {
        this.stopLoadingIndicator();
        this.router.navigateByUrl('/view');
      },
      (error: HttpErrorResponse) => {
        this.stopLoadingIndicator();
        if(error.status == 404) {
          this.displayError('The retrospective was not found.  Is the ID correct?');
         } else {
          this.displayError('Something bad happened.  Please contact us with the following information: [Status - ' + error.status + ', Message - ' + error.message + ']');
         }
      });
  }

  startLoadingIndicator(): void {
    this.joinButtonText = ' Joining...';
  }

  stopLoadingIndicator(): void {
    this.joinButtonText = 'Join';
  }

  displayError(errorMessage: string): void {
    this.errorText = errorMessage;
  }

  hideError(): void {
    this.errorText = '';
  }
}
