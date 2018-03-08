import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { HttpErrorResponse} from '@angular/common/http'
import { RetrospectiveService } from '../retrospective.service'

@Component({
  selector: 'app-join-retro',
  templateUrl: './join-retro.component.html',
  styleUrls: ['./join-retro.component.css']
})
export class JoinRetroComponent implements OnInit {

  errorText = '';

  constructor(private router: Router, private retroService: RetrospectiveService) { }

  ngOnInit() {
  }

  joinRetro(retroId: string, userName: string): void {
    this.retroService.joinRetrospective(retroId, userName)
      .subscribe(uuid => {
        this.router.navigateByUrl('/view');
      },
      (error: HttpErrorResponse) => {
        if(error.status == 404) {
          this.displayError('The retrospective was not found.  Is the ID correct?');
         } else {
          this.displayError('Something bad happened.  Please contact us with the following information: [Status - ' + error.status + ', Message - ' + error.message + ']');
         }
      });
  }

  displayError(errorMessage: string): void {
    this.errorText = errorMessage;
  }

  hideError(): void {
    this.errorText = '';
  }
}
