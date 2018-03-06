import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { StartRetroComponent } from './start-retro/start-retro.component'
import { JoinRetroComponent } from './join-retro/join-retro.component'

const routes: Routes = [
  { path: '', redirectTo: '/start', pathMatch: 'full' },
  { path: 'start', component: StartRetroComponent },
  { path: 'join', component: JoinRetroComponent }
]

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ],
})
export class AppRoutingModule { }
