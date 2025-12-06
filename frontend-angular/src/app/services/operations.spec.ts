import { TestBed } from '@angular/core/testing';

import { Operations } from './operations';

describe('Operations', () => {
  let service: Operations;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Operations);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
