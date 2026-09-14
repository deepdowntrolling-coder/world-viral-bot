name: World Viral Daily Bot - FULL AUTO
on:
  schedule:
    - cron: '0 5 * * *'
    - cron: '0 15 * * *'
  workflow_dispatch:
jobs:
  run-bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install
        run: |
          pip install -r requirements.txt
          sudo apt-get update
          sudo apt-get install -y ffmpeg
      - name: Run Bot and Upload
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          PEXELS_API_KEY: ${{ secrets.PEXELS_API_KEY }}
          YOUTUBE_CLIENT_ID: ${{ secrets.YOUTUBE_CLIENT_ID }}
          YOUTUBE_CLIENT_SECRET: ${{ secrets.YOUTUBE_CLIENT_SECRET }}
          YOUTUBE_REFRESH_TOKEN: ${{ secrets.YOUTUBE_REFRESH_TOKEN }}
        run: python main.py
      - name: Save video
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: video-${{ github.run_number }}
          path: |
            world_viral_output.mp4
            script.txt
