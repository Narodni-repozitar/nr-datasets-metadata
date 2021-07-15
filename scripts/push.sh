#!/usr/bin/env sh

TARGET=$1

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

commit_website_files() {
  git add -A
  git commit --message "Travis build: $TRAVIS_REPO_SLUG / $TRAVIS_BUILD_NUMBER"
}

upload_files() {
  git remote add origin-pages "https://${GH_TOKEN}@github.com/Narodni-repozitar/nr-schemas.git"
  git push --set-upstream origin-pages
}

cd $TARGET
setup_git
commit_website_files
upload_files