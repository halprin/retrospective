import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';


import { AppComponent } from './app.component';
import { NavigationBarComponent } from './navigation-bar/navigation-bar.component';
import { AppRoutingModule } from './/app-routing.module';
import { StartRetroComponent } from './start-retro/start-retro.component';
import { JoinRetroComponent } from './join-retro/join-retro.component';
import { ViewRetroComponent } from './view-retro/view-retro.component';


@NgModule({
  declarations: [
    AppComponent,
    NavigationBarComponent,
    StartRetroComponent,
    JoinRetroComponent,
    ViewRetroComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
